// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Visitor sandbox: runs the browser port of the STREAK engine in a Web Worker. Its
// output is labelled as sandbox output and never mixed with the published results.
// Nothing the visitor does is stored or sent anywhere.
import { useEffect, useRef, useState } from "react";
import type { WorkerReply, WorkerRequest } from "./sandbox.worker";
import type { Scenario } from "./results";
import { MAX_LEARNERS, type SandboxSummary } from "./sandboxStats";
import { Figure, Legend, LineChart, Timeline } from "./charts";

const ARM_LABEL: Record<string, string> = { A0: "A0 NoPractice", A1: "A1 Fixed", A2: "A2 Streak", A3: "A3 Spaced" };
const DEFAULTS = { seed: 1, learners: 100 };

export function Sandbox({ scenarios }: { scenarios: Scenario[] | null }) {
  const worker = useRef<Worker | null>(null);
  const [scenarioId, setScenarioId] = useState("default");
  const [seed, setSeed] = useState(DEFAULTS.seed);
  const [learners, setLearners] = useState(DEFAULTS.learners);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<SandboxSummary | null>(null);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") {
        setProgress(m.fraction);
        return;
      }
      if (m.type === "done") {
        setResult(m.result);
        setStatus(m.summary);
      }
      if (m.type === "error") setStatus(`The sandbox could not run: ${m.message}`);
      if (m.type === "cancelled") setStatus("Sandbox run cancelled.");
      setRunning(false);
    };
    worker.current = w;
    return () => w.terminate();
  }, []);

  const scenario = scenarios?.find((s) => s.id === scenarioId) ?? null;

  const run = () => {
    if (!scenario) return;
    setRunning(true);
    setProgress(0);
    setStatus(""); // the live region speaks again when the run ends
    worker.current?.postMessage({ type: "run", seed, learners, params: scenario.params, scenario: scenario.name } satisfies WorkerRequest);
  };
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    if (running) cancel();
    setScenarioId("default");
    setSeed(DEFAULTS.seed);
    setLearners(DEFAULTS.learners);
    setResult(null);
    setProgress(0);
    setStatus("Sandbox reset to the frozen default scenario, seed 1, 100 learners.");
  };

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <p className="label label-sandbox">Sandbox output</p>
      <h2 id="h-sandbox">Playground: run the model yourself</h2>
      <p>
        The sandbox runs a port of the research engine in your browser. Given identical random draws it reproduces the
        Python engine's review sequence exactly and its numbers to within 0.000000001 (tested on a fixture from the
        Python engine). It draws its own random numbers, so a sandbox seed is not a research seed and its numbers will
        not equal the published ones. <strong>Sandbox output is not a research result.</strong>
      </p>
      {scenarios === null ? (
        <p className="panel error" role="note">The sandbox needs the scenario list from the published results file, which did not load.</p>
      ) : (
        <form className="controls" onSubmit={(e) => { e.preventDefault(); run(); }}>
          <label>
            Scenario (assumption values)
            <select id="sb-scenario" value={scenarioId} onChange={(e) => setScenarioId(e.target.value)} disabled={running}>
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </label>
          <label>
            Seed
            <input id="sb-seed" type="number" inputMode="numeric" min={1} max={1_000_000} value={seed} disabled={running}
              onChange={(e) => setSeed(Math.min(1_000_000, Math.max(1, Math.round(Number(e.target.value)) || 1)))} />
          </label>
          <label>
            Synthetic learners (1 to {MAX_LEARNERS})
            <input id="sb-learners" type="number" inputMode="numeric" min={1} max={MAX_LEARNERS} value={learners} disabled={running}
              onChange={(e) => setLearners(Math.min(MAX_LEARNERS, Math.max(1, Math.round(Number(e.target.value)) || 1)))} />
          </label>
          <div className="buttons">
            <button id="sb-run" type="submit" disabled={running}>Run</button>
            <button id="sb-cancel" type="button" onClick={cancel} disabled={!running}>Cancel</button>
            <button id="sb-reset" type="button" onClick={reset}>Reset</button>
          </div>
        </form>
      )}
      {scenario && (
        <p className="meta">
          Scenario parameters: h0 = {scenario.params.h0} days, K = {scenario.params.n_items} items, q = {scenario.params.q},
          gain coefficient a = {scenario.params.a}, {scenario.params.form} forgetting, {scenario.params.gain_rule} gain.
          Source: <code>{scenario.source}</code>.
        </p>
      )}
      {running && <progress max={1} value={progress} aria-label="Sandbox progress" />}
      <p aria-live="polite" className="sandbox-out">{status}</p>
      {result && !running && <SandboxResult r={result} />}
    </section>
  );
}

function SandboxResult({ r }: { r: SandboxSummary }) {
  const T = r.horizon;
  const series = r.curves.map((c) => ({
    arm: c.arm,
    label: ARM_LABEL[c.arm],
    pts: c.values.map((y, x) => ({ x, y })),
  }));
  const timelineRows = r.timeline.filter((t) => t.arm !== "A0").map((t) => ({ ...t, label: ARM_LABEL[t.arm] }));
  const f3 = (x: number) => x.toFixed(3);
  return (
    <div className="sandbox-result">
      <p className="label label-sandbox">Sandbox output: {r.scenario}, seed {r.seed}, {r.learners} learners</p>
      <h3>Streak versus recall in this run</h3>
      <div id="tbl-sandbox" className="table-scroll" role="region" aria-label="Sandbox streak versus recall table" tabIndex={0}>
        <table>
          <thead>
            <tr>
              <th scope="col">Policy</th>
              <th scope="col">Mean active days</th>
              <th scope="col">Mean longest streak (days)</th>
              <th scope="col">Item coverage</th>
              <th scope="col">Mean R30 [approx. 95% interval]</th>
            </tr>
          </thead>
          <tbody>
            {r.arms.map((a) => (
              <tr key={a.arm}>
                <th scope="row">{ARM_LABEL[a.arm]}</th>
                <td>{a.activeDays.toFixed(2)}</td>
                <td>{a.longestStreak.toFixed(2)}</td>
                <td>{f3(a.coverage)}</td>
                <td>{f3(a.r30)} [{f3(a.r30Lo)}, {f3(a.r30Hi)}]</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ul className="diffs">
        {r.diffs.map((d) => (
          <li key={d.name}>
            {d.name.replace("A1", "A1 Fixed").replace("A2", "A2 Streak").replace("A3", "A3 Spaced")} in R30: <strong>{f3(d.mean)}</strong> [{f3(d.lo)}, {f3(d.hi)}]
          </li>
        ))}
      </ul>
      <p className="note">
        Intervals here are normal approximations over the sandbox learners (mean plus or minus 1.96 standard errors),
        simpler than the published bootstrap. They describe this run's noise only.
      </p>

      <Figure id="sb-timeline" title="Learning timeline: the first synthetic learner, day by day"
        desc={<>Each bar is one practice day; its height is the number of reviews that day. Small grey marks are days on which this learner was not available. A1 Fixed practises three days a week; A2 Streak and A3 Spaced practise every available day and therefore have identical timelines and streaks. Days 1 to {T}.</>}>
        <Timeline rows={timelineRows} horizon={T} />
      </Figure>

      <Figure id="sb-curves" title="Memory curves in this run: mean recall during and after practice"
        desc={<>Mean true recall over all items and sandbox learners, from day 0 (after the initial study) to {T} days of practice and 90 days after. The dashed vertical line marks the end of practice; R30 is read 30 days after it. Unit: proportion of items recalled.</>}>
        <Legend items={series.map((s) => ({ arm: s.arm, label: s.label }))} />
        <LineChart series={series} xLabel="Day" xMin={0} xMax={T + 90} yLabel="Mean recall"
          vline={{ x: T, label: "end of practice" }} ariaLabel="Sandbox memory curves per policy" />
      </Figure>
    </div>
  );
}
