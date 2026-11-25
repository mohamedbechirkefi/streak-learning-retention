// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
});

describe("STREAK extensions fail closed", () => {
  it("rejects a missing streak-versus-recall block", () => {
    const r = good();
    delete r.streak_vs_recall;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an R30 mean outside its interval", () => {
    const r = good();
    r.streak_vs_recall.arms[0].r30.mean = 2;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an inverted EXP-002 cell interval", () => {
    const r = good();
    const c = r.exp002_grid.cells[0];
    [c.ci_low, c.ci_high] = [c.ci_high, c.ci_low];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an EXP-003 effect without a display string", () => {
    const r = good();
    delete r.exp003_effects.variants[0].effects[0].display;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a calibration probability outside [0, 1]", () => {
    const r = good();
    r.heldout_calibration.bins[0].observed = 1.2;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects invalid or unbounded sandbox scenario parameters", () => {
    const r = good();
    r.sandbox_scenarios[0].params.q = 1.5;
    expect(() => validateResults(r)).toThrow(ResultsError);
    const r2 = good();
    r2.sandbox_scenarios[0].params.n_items = 5000;
    expect(() => validateResults(r2)).toThrow(ResultsError);
  });
  it("carries every experiment's evidence label and engine revision", () => {
    for (const e of validateResults(good()).experiments) {
      expect(e.label.length).toBeGreaterThan(0);
      expect(e.code_revision.length).toBeGreaterThan(0);
    }
  });
});
