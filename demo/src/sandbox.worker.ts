// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Bounded, cancellable sandbox: the browser port of the STREAK engine (src/engine.ts)
// run on synthetic learners drawn in the browser. Output is sandbox output, never a
// published result.
import { meanRetention, metrics, runLearner, drawLearner, validateParams, type Params } from "./engine";
import { MAX_LEARNERS, SANDBOX_ARMS, summarise, type SandboxSummary } from "./sandboxStats";

export type WorkerRequest =
  | { type: "run"; seed: number; learners: number; params: Params; scenario: string }
  | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; seed: number; summary: string; result: SandboxSummary }
  | { type: "cancelled" }
  | { type: "error"; message: string };

let cancelled = false;

async function simulate(seed: number, learners: number, params: Params, scenario: string): Promise<SandboxSummary | null> {
  validateParams(params);
  if (!Number.isInteger(seed) || seed < 1 || seed > 1_000_000) throw new Error("seed must be an integer from 1 to 1,000,000");
  if (!Number.isInteger(learners) || learners < 1 || learners > MAX_LEARNERS) throw new Error(`learners must be 1 to ${MAX_LEARNERS}`);
  if (params.n_items > 400) throw new Error("at most 400 items in the sandbox");
  const perArm = SANDBOX_ARMS.map(() => [] as ReturnType<typeof metrics>[]);
  const curves = SANDBOX_ARMS.map(() => new Float64Array(params.horizon_days + 1 + 90));
  const timeline: { arm: string; spent: number[]; available: boolean[] }[] = [];
  for (let j = 0; j < learners; j++) {
    const draws = drawLearner(seed, j, params);
    SANDBOX_ARMS.forEach((arm, a) => {
      const res = runLearner(draws, arm, params);
      perArm[a].push(metrics(res, params));
      const c = curves[a];
      res.dailyMeanRecall.forEach((v, d) => (c[d] += v / learners));
      // Post-practice memory curve, delays 1..90 days after day T.
      for (let delay = 1; delay <= 90; delay++) c[params.horizon_days + delay] += meanRetention(res, delay, params) / learners;
      if (j === 0) timeline.push({ arm, spent: res.dailySpent.slice(), available: res.available.slice() });
    });
    if (j % 10 === 9) {
      await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
      if (cancelled) return null;
      postMessage({ type: "progress", fraction: (j + 1) / learners } satisfies WorkerReply);
    }
  }
  return summarise(seed, scenario, params, [...SANDBOX_ARMS], perArm, curves.map((c) => Array.from(c)), timeline);
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    const result = await simulate(m.seed, m.learners, m.params, m.scenario);
    if (result === null) {
      postMessage({ type: "cancelled" } satisfies WorkerReply);
      return;
    }
    const d = result.diffs.find((x) => x.name === "A2 - A1")!;
    const summary = `Sandbox output, seed ${m.seed}, ${m.learners} synthetic learners: A2 Streak minus A1 Fixed in R30 = ${d.mean.toFixed(3)} (approximate 95% interval ${d.lo.toFixed(3)} to ${d.hi.toFixed(3)}).`;
    postMessage({ type: "done", seed: m.seed, summary, result } satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
