// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// The browser port against the Python engine (fixture from scripts/export_sandbox_fixture.py).
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { drawLearner, metrics, recall, runLearner, simulateArm, type Params } from "./engine";

const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8"));
const TOL = fx.tolerance_exact as number; // 1e-9, absolute

function maxAbsDiff(a: ArrayLike<number>, b: ArrayLike<number>): number {
  expect(a.length).toBe(b.length);
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
  return m;
}

describe("exact port on the Python engine's own random draws (tolerance 1e-9)", () => {
  it("fixture tolerance is 1e-9", () => expect(TOL).toBe(1e-9));
  for (const c of fx.exact) {
    const p = c.params as Params;
    for (const lr of c.learners) {
      for (const run of lr.runs) {
        it(`${c.name}, learner ${lr.learner_index}, ${run.arm}`, () => {
          const res = simulateArm(lr.h_init, lr.available, (d, i) => lr.outcome_u[d][i], run.arm, p);
          // Discrete trace: identical.
          expect(res.reviewDay).toEqual(run.review_day);
          expect(res.reviewItem).toEqual(run.review_item);
          expect(res.reviewSuccess.map(Number)).toEqual(run.review_success);
          expect(res.dailySpent).toEqual(run.daily_spent);
          expect(res.residual).toBe(run.residual);
          // Real-valued state: within tolerance.
          expect(maxAbsDiff(res.halfLife, run.half_life)).toBeLessThan(TOL);
          expect(maxAbsDiff(res.lastReview, run.last_review)).toBeLessThan(TOL);
          const m = metrics(res, p) as unknown as Record<string, number | null>;
          for (const [k, v] of Object.entries(run.metrics as Record<string, number | boolean | null>)) {
            if (k === "residual_flag") continue; // derived flag, not ported
            if (v === null) expect(m[k]).toBeNull();
            else expect(Math.abs((m[k] as number) - Number(v))).toBeLessThan(TOL);
          }
        });
      }
    }
  }
});

describe("forgetting curve bounds and budget conservation in the port", () => {
  it("recall is 1 at delay 0 and 0.5 at the half-life in both forms", () => {
    for (const f of ["exponential", "power"] as const) {
      expect(recall(0, 5, f)).toBe(1);
      expect(Math.abs(recall(5, 5, f) - 0.5)).toBeLessThan(1e-12);
    }
  });
  it("spent plus residual equals the budget for every practising arm", () => {
    const p = fx.population[0].params as Params;
    const draws = drawLearner(7, 0, p);
    for (const arm of ["A1", "A2", "A3"]) {
      const res = runLearner(draws, arm, p);
      expect(res.dailySpent.reduce((a, b) => a + b, 0) + res.residual).toBe(p.budget_slots);
    }
    expect(runLearner(draws, "A0", p).reviewDay.length).toBe(0);
  });
});

// The browser draws its own random numbers, so only population means are compared.
// Tolerances: about 4 standard errors of the difference between two independent
// means of n = 100 (Python) and n = 200 (browser) learners, using the Python SDs.
describe("population means with the browser's own random draws (Monte Carlo tolerance)", () => {
  for (const pc of fx.population) {
    it(`${pc.name}: arm means and paired differences`, () => {
      const p = pc.params as Params;
      const n = 200;
      const r30: Record<string, number[]> = { A0: [], A1: [], A2: [], A3: [] };
      for (let j = 0; j < n; j++) {
        const draws = drawLearner(424242, j, p);
        for (const arm of Object.keys(r30)) r30[arm].push(metrics(runLearner(draws, arm, p), p).R30);
      }
      const mean = (x: number[]) => x.reduce((a, b) => a + b, 0) / x.length;
      const se = (sd: number) => sd * Math.sqrt(1 / pc.n_learners + 1 / n);
      for (const arm of Object.keys(r30)) {
        const tol = Math.max(1e-6, 4 * se(pc.sd_R30[arm]));
        expect(Math.abs(mean(r30[arm]) - pc.mean_R30[arm])).toBeLessThan(tol);
      }
      for (const [name, a, b] of [["A2 - A1", "A2", "A1"], ["A3 - A1", "A3", "A1"]] as const) {
        const d = r30[a].map((v, i) => v - r30[b][i]);
        expect(Math.abs(mean(d) - pc.mean_diff[name])).toBeLessThan(4 * se(pc.sd_diff[name]));
      }
    });
  }
});
