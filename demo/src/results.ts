// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
import { validateParams, EngineError, type Params } from "./engine";

// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
  /** Kind of evidence: measured (confirmatory), real-data test or exploratory. */
  label: string;
  code_revision: string;
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  streak_vs_recall: StreakVsRecall;
  exp002_grid: Grid;
  exp003_effects: Effects;
  heldout_calibration: Calibration;
  sandbox_scenarios: Scenario[];
}

// ---------------- STREAK extensions (validated, fail closed) ----------------

export interface Shown {
  mean: number;
  display: string;
}
export interface CurvePoint {
  delay_days: number;
  mean: number;
  ci_low: number | null;
  ci_high: number | null;
  display: string;
}
export interface ArmProfile {
  arm: string;
  name: string;
  n: number;
  r30: { mean: number; ci_low: number; ci_high: number; display: string; interval_display: string };
  active_days: Shown;
  longest_streak: Shown;
  item_coverage: Shown;
  minutes: Shown;
  retention_curve: CurvePoint[];
}
export interface StreakVsRecall {
  experiment_id: string;
  note: string;
  arms: ArmProfile[];
}
export interface GridCell {
  cell_id: string;
  h0_days: number;
  a: number;
  q: number;
  estimate: number;
  ci_low: number;
  ci_high: number;
  display: string;
  interval_display: string;
  classification: string;
}
export interface Grid {
  experiment_id: string;
  contrast: string;
  sesoi: number;
  cells: GridCell[];
}
export interface Effect {
  effect: string;
  estimate: number;
  ci_low: number;
  ci_high: number;
  display: string;
  interval_display: string;
  classification: string;
}
export interface Effects {
  experiment_id: string;
  sesoi: number;
  variants: { variant: string; name: string; effects: Effect[] }[];
}
export interface CalibrationBin {
  bin: string;
  bin_low_days: number;
  bin_high_days: number;
  trials: number;
  observed: number;
  predicted_exponential: number;
  predicted_power: number;
  display_observed: string;
  display_exponential: string;
  display_power: string;
}
export interface Calibration {
  experiment_id: string;
  note: string;
  bins: CalibrationBin[];
}
export interface Scenario {
  id: string;
  name: string;
  source: string;
  params: Params;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

function interval(o: Obj, where: string, lo = "ci_low", hi = "ci_high"): [number, number] {
  const a = num(o, lo, where) as number;
  const b = num(o, hi, where) as number;
  if (a > b) throw new ResultsError(`${where}: ${lo} exceeds ${hi}`);
  return [a, b];
}

function nonEmpty<T>(xs: T[], where: string): T[] {
  if (xs.length === 0) throw new ResultsError(`${where}: empty`);
  return xs;
}

function shown(v: unknown, where: string): Shown {
  const o = obj(v, where);
  return { mean: num(o, "mean", where) as number, display: str(o, "display", where) };
}

function streakVsRecall(v: unknown): StreakVsRecall {
  const w = "streak_vs_recall";
  const o = obj(v, w);
  const arms = nonEmpty(arr(o, "arms", w), `${w}.arms`).map((x, i) => {
    const ww = `${w}.arms[${i}]`;
    const a = obj(x, ww);
    const r = obj(a.r30, `${ww}.r30`);
    const [lo, hi] = interval(r, `${ww}.r30`);
    const mean = num(r, "mean", `${ww}.r30`) as number;
    if (mean < lo || mean > hi) throw new ResultsError(`${ww}.r30: mean outside its interval`);
    const curve = nonEmpty(arr(a, "retention_curve", ww), `${ww}.retention_curve`).map((c, j) => {
      const wc = `${ww}.retention_curve[${j}]`;
      const co = obj(c, wc);
      const p: CurvePoint = {
        delay_days: num(co, "delay_days", wc) as number,
        mean: num(co, "mean", wc) as number,
        ci_low: num(co, "ci_low", wc, true),
        ci_high: num(co, "ci_high", wc, true),
        display: str(co, "display", wc),
      };
      if ((p.ci_low === null) !== (p.ci_high === null)) throw new ResultsError(`${wc}: half-open interval`);
      if (p.mean < 0 || p.mean > 1) throw new ResultsError(`${wc}: recall outside [0, 1]`);
      return p;
    });
    return {
      arm: str(a, "arm", ww),
      name: str(a, "name", ww),
      n: num(a, "n", ww) as number,
      r30: { mean, ci_low: lo, ci_high: hi, display: str(r, "display", ww), interval_display: str(r, "interval_display", ww) },
      active_days: shown(a.active_days, `${ww}.active_days`),
      longest_streak: shown(a.longest_streak, `${ww}.longest_streak`),
      item_coverage: shown(a.item_coverage, `${ww}.item_coverage`),
      minutes: shown(a.minutes, `${ww}.minutes`),
      retention_curve: curve,
    };
  });
  return { experiment_id: str(o, "experiment_id", w), note: str(o, "note", w), arms };
}

function grid(v: unknown): Grid {
  const w = "exp002_grid";
  const o = obj(v, w);
  const cells = nonEmpty(arr(o, "cells", w), `${w}.cells`).map((x, i) => {
    const ww = `${w}.cells[${i}]`;
    const c = obj(x, ww);
    const [lo, hi] = interval(c, ww);
    return {
      cell_id: str(c, "cell_id", ww),
      h0_days: num(c, "h0_days", ww) as number,
      a: num(c, "a", ww) as number,
      q: num(c, "q", ww) as number,
      estimate: num(c, "estimate", ww) as number,
      ci_low: lo,
      ci_high: hi,
      display: str(c, "display", ww),
      interval_display: str(c, "interval_display", ww),
      classification: str(c, "classification", ww),
    };
  });
  return { experiment_id: str(o, "experiment_id", w), contrast: str(o, "contrast", w), sesoi: num(o, "sesoi", w) as number, cells };
}

function effects(v: unknown): Effects {
  const w = "exp003_effects";
  const o = obj(v, w);
  const variants = nonEmpty(arr(o, "variants", w), `${w}.variants`).map((x, i) => {
    const ww = `${w}.variants[${i}]`;
    const vo = obj(x, ww);
    return {
      variant: str(vo, "variant", ww),
      name: str(vo, "name", ww),
      effects: nonEmpty(arr(vo, "effects", ww), `${ww}.effects`).map((y, j) => {
        const we = `${ww}.effects[${j}]`;
        const e = obj(y, we);
        const [lo, hi] = interval(e, we);
        return {
          effect: str(e, "effect", we), estimate: num(e, "estimate", we) as number, ci_low: lo, ci_high: hi,
          display: str(e, "display", we), interval_display: str(e, "interval_display", we),
          classification: str(e, "classification", we),
        };
      }),
    };
  });
  return { experiment_id: str(o, "experiment_id", w), sesoi: num(o, "sesoi", w) as number, variants };
}

function calibration(v: unknown): Calibration {
  const w = "heldout_calibration";
  const o = obj(v, w);
  const bins = nonEmpty(arr(o, "bins", w), `${w}.bins`).map((x, i) => {
    const ww = `${w}.bins[${i}]`;
    const b = obj(x, ww);
    const [lo, hi] = interval(b, ww, "bin_low_days", "bin_high_days");
    const prob = (k: string) => {
      const p = num(b, k, ww) as number;
      if (p < 0 || p > 1) throw new ResultsError(`${ww}.${k}: outside [0, 1]`);
      return p;
    };
    return {
      bin: str(b, "bin", ww), bin_low_days: lo, bin_high_days: hi, trials: num(b, "trials", ww) as number,
      observed: prob("observed"), predicted_exponential: prob("predicted_exponential"), predicted_power: prob("predicted_power"),
      display_observed: str(b, "display_observed", ww), display_exponential: str(b, "display_exponential", ww),
      display_power: str(b, "display_power", ww),
    };
  });
  return { experiment_id: str(o, "experiment_id", w), note: str(o, "note", w), bins };
}

function scenarios(o: Obj): Scenario[] {
  return nonEmpty(arr(o, "sandbox_scenarios", "results"), "results.sandbox_scenarios").map((x, i) => {
    const w = `sandbox_scenarios[${i}]`;
    const s = obj(x, w);
    const params = obj(s.params, `${w}.params`) as unknown as Params;
    try {
      validateParams(params);
    } catch (e) {
      throw new ResultsError(`${w}.params: ${e instanceof EngineError ? e.message : "invalid"}`);
    }
    if (params.n_items > 400) throw new ResultsError(`${w}.params.n_items: above the sandbox bound of 400`);
    return { id: str(s, "id", w), name: str(s, "name", w), source: str(s, "source", w), params };
  });
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
      label: str(e, "label", w),
      code_revision: str(e, "code_revision", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    streak_vs_recall: streakVsRecall(o.streak_vs_recall),
    exp002_grid: grid(o.exp002_grid),
    exp003_effects: effects(o.exp003_effects),
    heldout_calibration: calibration(o.heldout_calibration),
    sandbox_scenarios: scenarios(o),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "no interval";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
