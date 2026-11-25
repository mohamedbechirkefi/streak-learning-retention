// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Summary of one sandbox run. Intervals are normal approximations (mean plus or minus
// 1.96 standard errors over learners), a simpler method than the published stratified
// bootstrap; they describe sandbox noise only.
import type { Metrics, Params } from "./engine";

export const MAX_LEARNERS = 200;
export const SANDBOX_ARMS = ["A0", "A1", "A2", "A3"] as const;

export interface ArmSummary {
  arm: string;
  r30: number;
  r30Lo: number;
  r30Hi: number;
  activeDays: number;
  longestStreak: number;
  coverage: number;
  minutes: number;
}
export interface DiffSummary {
  name: string;
  mean: number;
  lo: number;
  hi: number;
}
export interface SandboxSummary {
  seed: number;
  scenario: string;
  learners: number;
  horizon: number;
  arms: ArmSummary[];
  diffs: DiffSummary[];
  /** Mean true recall per arm on days 0..T (practice) and T+1..T+90 (after practice). */
  curves: { arm: string; values: number[] }[];
  /** Day-by-day slots for the first synthetic learner. */
  timeline: { arm: string; spent: number[]; available: boolean[] }[];
}

const mean = (x: number[]) => x.reduce((a, b) => a + b, 0) / x.length;

export function meanCi(x: number[]): [number, number, number] {
  const m = mean(x);
  if (x.length < 2) return [m, m, m];
  const v = x.reduce((a, b) => a + (b - m) ** 2, 0) / (x.length - 1);
  const h = 1.96 * Math.sqrt(v / x.length);
  return [m, m - h, m + h];
}

export function summarise(seed: number, scenario: string, params: Params, arms: string[], perArm: Metrics[][],
  curves: number[][], timeline: SandboxSummary["timeline"]): SandboxSummary {
  const r30 = perArm.map((ms) => ms.map((m) => m.R30));
  const armSummaries = arms.map((arm, a) => {
    const [m, lo, hi] = meanCi(r30[a]);
    return {
      arm, r30: m, r30Lo: lo, r30Hi: hi,
      activeDays: mean(perArm[a].map((x) => x.active_days)),
      longestStreak: mean(perArm[a].map((x) => x.longest_streak)),
      coverage: mean(perArm[a].map((x) => x.item_coverage)),
      minutes: mean(perArm[a].map((x) => x.minutes_spent)),
    };
  });
  const idx = (name: string) => arms.indexOf(name);
  const diffs = ([["A2", "A1"], ["A3", "A1"], ["A2", "A3"]] as const).map(([x, y]) => {
    const d = r30[idx(x)].map((v, i) => v - r30[idx(y)][i]);
    const [m, lo, hi] = meanCi(d);
    return { name: `${x} - ${y}`, mean: m, lo, hi };
  });
  return {
    seed, scenario, learners: r30[0].length, horizon: params.horizon_days,
    arms: armSummaries, diffs, curves: arms.map((arm, a) => ({ arm, values: curves[a] })), timeline,
  };
}
