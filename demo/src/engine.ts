// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Browser port of the STREAK simulation step (src/streak/memory.py, simulate.py,
// metrics.py, engine 1.1.0). Given the same random draws, it reproduces the Python
// engine's review trace exactly and its real-valued outputs within 1e-9
// (src/engine.test.ts against src/fixtures/engine_fixture.json).
// The learner draws (drawLearner) use a browser generator, not NumPy's, so a sandbox
// seed is not a research seed and sandbox numbers do not reproduce published ones.

export type Form = "exponential" | "power";
export type GainRule = "difficulty" | "flat";
export type Timing = "none" | "daily" | "fixed";
export type Selection = "none" | "round_robin" | "easiest" | "due_threshold";

export interface Params {
  n_items: number;
  horizon_days: number;
  budget_slots: number;
  slot_minutes: number;
  daily_cap_slots: number;
  fixed_weekdays: number[];
  h0: number;
  sigma_item: number;
  sigma_learner: number;
  g_min: number;
  a: number;
  b: number;
  h_min: number;
  q: number;
  form: Form;
  gain_rule: GainRule;
}

export const ARMS: Record<string, { timing: Timing; selection: Selection }> = {
  A0: { timing: "none", selection: "none" },
  A1: { timing: "fixed", selection: "round_robin" },
  A2: { timing: "daily", selection: "easiest" },
  A3: { timing: "daily", selection: "due_threshold" },
  "D-RR": { timing: "daily", selection: "round_robin" },
  "F-EASY": { timing: "fixed", selection: "easiest" },
  "F-DUE": { timing: "fixed", selection: "due_threshold" },
};

const DUE_TARGET = 0.9;
const POWER_C = 3.0;
const POWER_EXPONENT = -0.5;
export const RETENTION_DELAYS = [1, 7, 30, 90];
export const AUC_MAX_DELAY = 90;

export class EngineError extends Error {}

export function recall(delay: number, h: number, form: Form): number {
  if (!(delay >= 0) || !(h > 0) || !Number.isFinite(delay) || !Number.isFinite(h)) {
    throw new EngineError("delay must be finite and non-negative, half-life finite and positive");
  }
  const p = form === "exponential" ? Math.pow(2, -delay / h) : Math.pow(1 + (POWER_C * delay) / h, POWER_EXPONENT);
  return Math.min(1, Math.max(0, p));
}

export function updatedHalfLife(h: number, p: number, success: boolean, gain: GainRule, prm: Params): number {
  if (!success) return Math.max(prm.h_min, prm.b * h);
  const factor = gain === "difficulty" ? 1 + prm.g_min + prm.a * (1 - p) : 1 + prm.g_min + prm.a * 0.3;
  return h * factor;
}

export function validateParams(p: Params): void {
  const intPos = (k: keyof Params) => {
    const v = p[k] as number;
    if (!Number.isInteger(v) || v < 1) throw new EngineError(`${k} must be a positive integer`);
  };
  intPos("n_items");
  intPos("horizon_days");
  intPos("daily_cap_slots");
  if (!Number.isInteger(p.budget_slots) || p.budget_slots < 0) throw new EngineError("budget_slots must be a non-negative integer");
  for (const k of ["slot_minutes", "h0", "h_min", "a"] as const) {
    if (!(p[k] > 0) || !Number.isFinite(p[k])) throw new EngineError(`${k} must be finite and positive`);
  }
  for (const k of ["sigma_item", "sigma_learner", "g_min"] as const) {
    if (!(p[k] >= 0) || !Number.isFinite(p[k])) throw new EngineError(`${k} must be finite and non-negative`);
  }
  if (!(p.b > 0 && p.b < 1)) throw new EngineError("b must lie in (0, 1)");
  if (!(p.q >= 0 && p.q <= 1)) throw new EngineError("q must lie in [0, 1]");
  if (p.form !== "exponential" && p.form !== "power") throw new EngineError("unknown forgetting form");
  if (p.gain_rule !== "difficulty" && p.gain_rule !== "flat") throw new EngineError("unknown gain rule");
}

export function plannedSlots(timing: Timing, p: Params): number[] {
  const plan = new Array<number>(p.horizon_days + 1).fill(0);
  if (timing === "none") return plan;
  const days: number[] = [];
  for (let d = 1; d <= p.horizon_days; d++) {
    if (timing === "daily" || p.fixed_weekdays.includes(d % 7)) days.push(d);
  }
  if (days.length === 0) throw new EngineError("timing has no scheduled day within the horizon");
  if (p.budget_slots % days.length) throw new EngineError("budget is not divisible by the scheduled days");
  for (const d of days) plan[d] = p.budget_slots / days.length;
  return plan;
}

/** Mirrors simulate.select_items, including NumPy's stable tie-breaking (lower index first). */
export function selectItems(selection: Selection, n: number, pHat: Float64Array, rr: number): [number[], number] {
  const k = pHat.length;
  if (n < 0 || n > k) throw new EngineError(`cannot select ${n} distinct items out of ${k}`);
  if (selection === "round_robin") {
    const idx: number[] = [];
    for (let j = 0; j < n; j++) idx.push((rr + j) % k);
    return [idx, (rr + n) % k];
  }
  const order = Array.from({ length: k }, (_, i) => i);
  if (selection === "easiest") {
    order.sort((i, j) => pHat[j] - pHat[i] || i - j);
  } else if (selection === "due_threshold") {
    order.sort((i, j) => {
      const di = pHat[i] <= DUE_TARGET ? 0 : 1;
      const dj = pHat[j] <= DUE_TARGET ? 0 : 1;
      if (di !== dj) return di - dj;
      const ki = di === 0 ? -pHat[i] : pHat[i];
      const kj = dj === 0 ? -pHat[j] : pHat[j];
      return ki - kj || i - j;
    });
  } else {
    throw new EngineError(`unknown selection ${selection}`);
  }
  return [order.slice(0, n), rr];
}

export interface ArmResult {
  halfLife: Float64Array;
  lastReview: Float64Array;
  dailySpent: number[];
  residual: number;
  available: boolean[];
  reviewDay: number[];
  reviewItem: number[];
  reviewSuccess: boolean[];
  /** Mean true recall over all items at the end of each day 0..T (0: just after initial study). */
  dailyMeanRecall: number[];
}

export function simulateArm(hInit: ArrayLike<number>, available: ArrayLike<boolean | number>,
  outcomeU: (d: number, i: number) => number, armName: string, p: Params): ArmResult {
  const arm = ARMS[armName];
  if (!arm) throw new EngineError(`unknown arm ${armName}`);
  const k = p.n_items;
  const T = p.horizon_days;
  if (hInit.length !== k) throw new EngineError("h_init must have K entries");
  if (available.length !== T + 1) throw new EngineError("available must have length T + 1");
  const h = Float64Array.from(hInit);
  const s = new Float64Array(k);
  const hHat = new Float64Array(k).fill(p.h0);
  const plan = plannedSlots(arm.timing, p);
  const spent = new Array<number>(T + 1).fill(0);
  const av = Array.from({ length: T + 1 }, (_, d) => Boolean(available[d]));
  const maxPerDay = Math.min(p.daily_cap_slots, k);
  const reviewDay: number[] = [], reviewItem: number[] = [], reviewSuccess: boolean[] = [];
  const meanRecallAt = (t: number) => {
    let acc = 0;
    for (let i = 0; i < k; i++) acc += recall(t - s[i], h[i], p.form);
    return acc / k;
  };
  const dailyMeanRecall = [meanRecallAt(0)];
  let pending = 0;
  let rr = 0;
  const pHat = new Float64Array(k);
  for (let d = 1; d <= T; d++) {
    pending += plan[d];
    if (av[d] && pending > 0) {
      const n = Math.min(pending, maxPerDay);
      for (let i = 0; i < k; i++) pHat[i] = recall(d - s[i], hHat[i], "exponential");
      const [idx, nextRr] = selectItems(arm.selection, n, pHat, rr);
      rr = nextRr;
      for (const i of idx) {
        const pTrue = recall(d - s[i], h[i], p.form);
        const ok = outcomeU(d, i) < pTrue;
        h[i] = updatedHalfLife(h[i], pTrue, ok, p.gain_rule, p);
        hHat[i] = updatedHalfLife(hHat[i], pHat[i], ok, "difficulty", p);
        s[i] = d;
        reviewDay.push(d);
        reviewItem.push(i);
        reviewSuccess.push(ok);
      }
      spent[d] = n;
      pending -= n;
    }
    dailyMeanRecall.push(meanRecallAt(d));
  }
  return { halfLife: h, lastReview: s, dailySpent: spent, residual: pending, available: av,
    reviewDay, reviewItem, reviewSuccess, dailyMeanRecall };
}

export function meanRetention(res: ArmResult, delay: number, p: Params): number {
  const t = p.horizon_days + delay;
  let acc = 0;
  for (let i = 0; i < p.n_items; i++) acc += recall(t - res.lastReview[i], res.halfLife[i], p.form);
  return acc / p.n_items;
}

export interface Metrics {
  R1: number; R7: number; R30: number; R90: number; AUC_R: number; weakest_decile_R30: number;
  minutes_spent: number; slots_spent: number; residual_slots: number; reviews: number;
  active_days: number; longest_streak: number; final_streak: number;
  missed_unavailable_days: number; missed_available_days: number;
  practice_success_rate: number | null; item_coverage: number;
}

/** Python's round(): halves go to the even neighbour. */
function roundHalfEven(x: number): number {
  const f = Math.floor(x);
  const diff = x - f;
  if (diff > 0.5) return f + 1;
  if (diff < 0.5) return f;
  return f % 2 === 0 ? f : f + 1;
}

export function metrics(res: ArmResult, p: Params): Metrics {
  const T = p.horizon_days;
  const r = (d: number) => meanRetention(res, d, p);
  let auc = 0;
  for (let d = 0; d <= AUC_MAX_DELAY; d++) auc += r(d);
  const r30Items: number[] = [];
  for (let i = 0; i < p.n_items; i++) r30Items.push(recall(T + 30 - res.lastReview[i], res.halfLife[i], p.form));
  r30Items.sort((x, y) => x - y);
  const nDec = Math.max(1, roundHalfEven(0.1 * p.n_items));
  let weakest = 0;
  for (let i = 0; i < nDec; i++) weakest += r30Items[i];
  let slots = 0, active = 0, longest = 0, cur = 0, missedUnavail = 0, missedAvail = 0;
  for (let d = 1; d <= T; d++) {
    slots += res.dailySpent[d];
    const isActive = res.dailySpent[d] > 0;
    if (isActive) active++;
    cur = isActive ? cur + 1 : 0;
    longest = Math.max(longest, cur);
    if (!res.available[d]) missedUnavail++;
    else if (!isActive) missedAvail++;
  }
  const nRev = res.reviewDay.length;
  const succ = res.reviewSuccess.reduce((acc, v) => acc + (v ? 1 : 0), 0);
  return {
    R1: r(1), R7: r(7), R30: r(30), R90: r(90), AUC_R: auc / (AUC_MAX_DELAY + 1), weakest_decile_R30: weakest / nDec,
    minutes_spent: slots * p.slot_minutes, slots_spent: slots, residual_slots: res.residual, reviews: nRev,
    active_days: active, longest_streak: longest, final_streak: cur,
    missed_unavailable_days: missedUnavail, missed_available_days: missedAvail,
    practice_success_rate: nRev ? succ / nRev : null, item_coverage: new Set(res.reviewItem).size / p.n_items,
  };
}

// ---------------- Browser random draws (not NumPy's generator) ----------------

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(rng: () => number): number {
  // Box-Muller; 1 - u keeps the logarithm finite.
  const u = 1 - rng();
  const v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

export interface LearnerDraws {
  hInit: Float64Array;
  available: boolean[];
  outcome: Float64Array; // (T + 1) x K, row-major
}

/** One synthetic learner, with the same distributions as src/streak/population.py. */
export function drawLearner(seed: number, index: number, p: Params): LearnerDraws {
  const mix = (x: number) => (Math.imul(x ^ (x >>> 16), 0x45d9f3b) ^ index * 0x9e3779b1) >>> 0;
  const rAbility = mulberry32(mix(seed * 3 + 1));
  const rAvail = mulberry32(mix(seed * 3 + 2));
  const rOutcome = mulberry32(mix(seed * 3 + 3));
  const theta = Math.exp(p.sigma_learner * normal(rAbility));
  const hInit = new Float64Array(p.n_items);
  for (let i = 0; i < p.n_items; i++) hInit[i] = p.h0 * Math.exp(p.sigma_item * normal(rAbility)) * theta;
  const available = Array.from({ length: p.horizon_days + 1 }, (_, d) => {
    const u = rAvail();
    return d > 0 && u < p.q;
  });
  const outcome = new Float64Array((p.horizon_days + 1) * p.n_items);
  for (let j = 0; j < outcome.length; j++) outcome[j] = rOutcome();
  return { hInit, available, outcome };
}

export function runLearner(draws: LearnerDraws, arm: string, p: Params): ArmResult {
  return simulateArm(draws.hInit, draws.available, (d, i) => draws.outcome[d * p.n_items + i], arm, p);
}
