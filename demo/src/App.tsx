// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
import { useEffect, useRef, useState, type ReactNode } from "react";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";
import { Figure, ForestChart, Legend, LineChart, StreakRecallChart } from "./charts";
import { HeroBook, ReportCard } from "./brand";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <SiteBar />
      <main id="main">
        <Hero />
        <div className="wrap">
          {state.kind === "loading" && <p role="status">Loading the published results.</p>}
          {state.kind === "error" && (
            <div role="alert" className="panel error">
              <h2>Results unavailable</h2>
              <p>The published results file failed validation, so no numbers are shown.</p>
              <p><code>{state.message}</code></p>
            </div>
          )}
          {state.kind === "ready" && <Published r={state.results} />}
          <Sandbox scenarios={state.kind === "ready" ? state.results.sandbox_scenarios : null} />
          {state.kind === "ready" && <Background r={state.results} />}
          <Reproduce />
        </div>
      </main>
      <Footer />
    </>
  );
}

const SECTIONS: [string, string][] = [
  ["overview", "Report card"],
  ["streak-recall", "Streak versus recall"],
  ["memory", "Memory curves"],
  ["results", "Results"],
  ["sandbox", "Playground"],
  ["assumptions", "Assumptions"],
  ["method", "Limitations"],
  ["reproduce", "Reproduce"],
];

/** Sticky bar: lockup and section links; a marigold indicator slides to the section in view. */
function SiteBar() {
  const navRef = useRef<HTMLElement | null>(null);
  const indRef = useRef<HTMLSpanElement | null>(null);
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;
    const seen = new Map<string, boolean>();
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) seen.set(e.target.id, e.isIntersecting);
      const first = SECTIONS.find(([id]) => seen.get(id));
      setActive(first ? first[0] : null);
    }, { rootMargin: "-30% 0px -60% 0px" });
    const observeAll = () => SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    observeAll();
    const t = window.setTimeout(observeAll, 1200); // sections that mount after the results load
    return () => { io.disconnect(); window.clearTimeout(t); };
  }, []);

  useEffect(() => {
    const nav = navRef.current, ind = indRef.current;
    if (!nav || !ind) return;
    const a = active ? nav.querySelector<HTMLAnchorElement>(`a[href="#${active}"]`) : null;
    if (!a) { ind.style.opacity = "0"; return; }
    ind.style.opacity = "1";
    ind.style.transform = `translateX(${a.offsetLeft + 10}px) scaleX(${(a.offsetWidth - 20) / 100})`;
    if (nav.scrollWidth > nav.clientWidth) {
      const target = a.offsetLeft - nav.clientWidth / 2 + a.offsetWidth / 2;
      nav.scrollTo({ left: target, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    }
  }, [active]);

  return (
    <header className="bar">
      <div className="wrap bar-in">
        <a className="brand" href="#top" aria-label="Streak, back to the top">
          <img src="brand/streak-lockup.svg" alt="" width="118" height="26" />
        </a>
        <nav className="sections" aria-label="Sections" ref={navRef}>
          <ul>
            {SECTIONS.map(([id, label]) => (
              <li key={id}><a href={`#${id}`} aria-current={active === id ? "true" : undefined}>{label}</a></li>
            ))}
          </ul>
          <span className="ind" ref={indRef} aria-hidden="true" />
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <div className="hero" id="top">
      <div className="wrap hero-grid">
        <div>
          <h1>When can activity streaks diverge from knowledge retention in a learning model?</h1>
          <p className="answer">
            <strong>In this model, when keeping the streak also means practising the easiest items.</strong> With the same
            practice time, a streak-driven policy practised on about twice as many days as a fixed schedule and recalled
            much less 30 days later; the cost came from which items were practised, not from practising every day.
          </p>
          <p className="status">
            The gap reversed sign in a near-total-forgetting regime, and a held-out test on real data did not support
            the model's forgetting curve. These findings are properties of the model, not of real learners.
          </p>
          <p className="byline">Mohamed Bechir Kefi, independent researcher. A simulation of synthetic learners, not of people.</p>
        </div>
        <HeroBook />
      </div>
    </div>
  );
}

function Reproduce() {
  return (
    <section id="reproduce" aria-labelledby="h-reproduce">
      <h2 id="h-reproduce">Reproduce</h2>
      <p className="prose">
        Everything on this page is regenerated from the repository. The Python suite checks that the numbers shown
        here are the ones printed in the manuscript and reports.
      </p>
      <pre className="cmd"><code>{`uv sync --frozen
.venv/bin/python -m pytest
.venv/bin/python scripts/run_confirmatory.py EXP-001
.venv/bin/python scripts/analyse_confirmatory.py EXP-001
cd demo && npm ci && npm test && npm run build`}</code></pre>
    </section>
  );
}

const REPO = "https://github.com/mohamedbechirkefi/streak-learning-retention";

function Footer() {
  return (
    <footer className="site">
      <div className="wrap foot-grid">
        <div>
          <img src="brand/streak-lockup.svg" alt="Streak" width="127" height="28" />
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere, and there
            are no accounts, trackers or external fonts. The page has no streaks, rewards, reminders or prompts to
            return: it describes streaks, it does not use them.
          </p>
          <p>Simulated learners are not people. Nothing on this page is evidence about real human learning or about any real product.</p>
          <p>Mohamed Bechir Kefi, independent researcher.</p>
          <p className="small">
            STREAK Source-Available Non-Commercial Research License v1.0 (LicenseRef-STREAK-NC-Research-1.0), a custom
            licence that is not OSI approved. AI assistance is disclosed: the AI acts as a research and development
            assistant; the owner holds authority over hypotheses, protocol freezes, claims and publication.
          </p>
        </div>
        <div>
          <ul>
            <li><a href={REPO}>Source code on GitHub</a></li>
            <li><a href={`${REPO}/blob/main/research/paper/manuscript.md`}>Manuscript</a></li>
            <li><a href="https://labs.kefimohamedbechir.workers.dev">All lab studies</a></li>
          </ul>
          <p className="small">
            Typefaces: Bricolage Grotesque (The Bricolage Grotesque Project Authors) and Nunito Sans (The Nunito Sans
            Project Authors), both under the SIL Open Font License, version 1.1, self-hosted.
          </p>
        </div>
      </div>
    </footer>
  );
}

const LABEL_CLASS = (label: string) =>
  label.startsWith("measured (confirmatory") ? "label-measured" : label.startsWith("measured (real") ? "label-realdata" : "label-exploratory";

function Published({ r }: { r: Results }) {
  const arms = r.streak_vs_recall.arms;
  const by = (a: string) => arms.find((x) => x.arm === a)!;
  const [a1, a2, a3] = [by("A1"), by("A2"), by("A3")];
  const exp1 = r.experiments.find((e) => e.id === "EXP-001")!;
  const primary = exp1.estimates[0];

  const svr = (metric: "active_days" | "longest_streak") =>
    arms.map((a) => ({
      arm: a.arm, label: a.name, x: a[metric].mean, y: a.r30.mean, lo: a.r30.ci_low, hi: a.r30.ci_high,
      xText: a[metric].display, yText: a.r30.display,
    }));
  const curves = arms.map((a) => ({
    arm: a.arm, label: a.name,
    pts: a.retention_curve.map((p) => ({ x: p.delay_days, y: p.mean, lo: p.ci_low, hi: p.ci_high })),
  }));
  const cal = r.heldout_calibration;
  const [axis, setAxis] = useState("days");
  const mid = (b: { bin_low_days: number; bin_high_days: number }) => Math.sqrt(b.bin_low_days * b.bin_high_days);

  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <p className="label label-measured">Measured, confirmatory simulation, EXP-001</p>
        <h2 id="h-overview">The report card</h2>
        <p className="lede">
          Activity streaks count consecutive days with practice. In a preregistered simulation with the same practice
          time for every policy, a stylised streak-driven policy (practise every available day, easiest items first)
          was compared with a fixed three-sessions-per-week schedule, a threshold-based spaced-repetition comparator and
          a no-practice control.
        </p>
        <ReportCard arms={arms} />
        <div className="margin-notes">
          <div className="mnote">
            <p className="fact-big">{primary.display}</p>
            <p>difference in mean recall 30 days after practice, A2 Streak minus A1 Fixed ({fmtInterval(primary)}).</p>
          </div>
          <div className="mnote">
            <p className="fact-big">{a2.active_days.display} <span className="vs">vs</span> {a1.active_days.display}</p>
            <p>mean active days, A2 Streak against A1 Fixed: about twice the activity, with much lower recall.</p>
          </div>
          <div className="mnote">
            <p className="fact-big">{a3.r30.display} <span className="vs">vs</span> {a2.r30.display}</p>
            <p>mean R30 of A3 Spaced against A2 Streak, which have exactly the same active days and streaks.</p>
          </div>
        </div>
        <p className="prose">
          In this model the retention cost came from <em>which items</em> were practised (easiest first), not from
          practising every day (EXP-003). The gap reversed sign in a near-total-forgetting regime, and a held-out test on
          real data did not support the model's forgetting curve (see Memory curves and the published results below).
        </p>
        <p className="status-label meta"><strong>Status.</strong> {r.status_label}</p>
      </section>

      <section id="streak-recall" aria-labelledby="h-svr">
        <p className="label label-measured">Measured, confirmatory simulation, EXP-001</p>
        <h2 id="h-svr">Streak versus recall</h2>
        <p className="note">{r.streak_vs_recall.note}</p>
        <Segmented label="Horizontal axis" options={[["days", "Active days"], ["streak", "Longest streak"]]} value={axis} onChange={setAxis} />
        <div hidden={axis !== "days"}>
          <Figure id="f-svr-days" title="Active days against R30"
            desc={<>Each mark is one policy: horizontal position is the mean number of days with practice (out of 56), vertical position is mean R30 with its 95% interval (the vertical bar, narrower than the mark here). A2 Streak and A3 Spaced sit at the same activity, {a2.active_days.display} days, yet differ by about 0.3 in recall.</>}>
            <StreakRecallChart points={svr("active_days")} xLabel="Mean active days" xMax={56} />
          </Figure>
        </div>
        <div hidden={axis !== "streak"}>
          <Figure id="f-svr-streak" title="Longest streak against R30"
            desc={<>The same policies with the mean longest run of consecutive practice days on the horizontal axis. The longest streak, {a2.longest_streak.display} days for A2 Streak against {a1.longest_streak.display} for A1 Fixed, says nothing about which policy retained more.</>}>
            <StreakRecallChart points={svr("longest_streak")} xLabel="Mean longest streak (days)" xMax={20} />
          </Figure>
        </div>
        <Legend items={arms.map((a) => ({ arm: a.arm, label: a.name }))} />
        <div id="tbl-svr" className="table-scroll" role="region" aria-label="Streak versus recall table" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">Policy</th>
                <th scope="col">R30 [95% CI]</th>
                <th scope="col">Active days</th>
                <th scope="col">Longest streak (days)</th>
                <th scope="col">Item coverage</th>
                <th scope="col">Minutes</th>
              </tr>
            </thead>
            <tbody>
              {arms.map((a) => (
                <tr key={a.arm}>
                  <th scope="row">{a.name}</th>
                  <td>{a.r30.display} {a.r30.interval_display}</td>
                  <td>{a.active_days.display}</td>
                  <td>{a.longest_streak.display}</td>
                  <td>{a.item_coverage.display}</td>
                  <td>{a.minutes.display}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section id="memory" aria-labelledby="h-memory">
        <h2 id="h-memory">Memory curves</h2>
        <div className="two">
          <Figure id="f-mem" title="Model: mean recall after practice ends (EXP-001)"
            desc={<>Mean expected recall 1, 7, 30 and 90 days after the 56-day practice period, per policy, 1,000 synthetic learners each. Only R30 has an interval (vertical bars, very short at this sample size); the committed outputs have no interval for the other delays. Unit: proportion of items recalled.</>}>
            <p className="label label-measured">Measured, confirmatory simulation</p>
            <Legend items={arms.map((a) => ({ arm: a.arm, label: a.name }))} />
            <LineChart series={curves} xLabel="Days after practice ends" xMin={0} xMax={90} yLabel="Mean recall" marks ariaLabel="Mean recall at 1, 7, 30 and 90 days after practice, per policy" />
          </Figure>
          <Figure id="f-cal" title="Real data: the forgetting curve did not fit (held-out test)"
            desc={<>Observed recall on held-out Duolingo first repeats, by delay bin, against the recall each fitted forgetting form predicts. Observed recall falls only from {cal.bins[0].display_observed} to {cal.bins[cal.bins.length - 1].display_observed}, much flatter than either form. This is a negative result for the model's assumption. The data are in-session accuracy of users of one product, not free recall.</>}>
            <p className="label label-realdata">Measured, real public data, descriptive test</p>
            <Legend items={[{ arm: "A0", label: "Observed" }, { arm: "A1", label: "Exponential form (model default)" }, { arm: "A2", label: "Power-law form" }]} />
            <LineChart
              series={[
                { arm: "A0", label: "Observed", pts: cal.bins.map((b) => ({ x: mid(b), y: b.observed })) },
                { arm: "A1", label: "Exponential", pts: cal.bins.map((b) => ({ x: mid(b), y: b.predicted_exponential })) },
                { arm: "A2", label: "Power law", pts: cal.bins.map((b) => ({ x: mid(b), y: b.predicted_power })) },
              ]}
              xLabel="Delay since first exposure (days, bin midpoint)" xMin={0} xMax={60} yMin={0.5} yLabel="Recall" marks
              ariaLabel="Observed against predicted recall by delay bin" />
            <div id="tbl-cal" className="table-scroll" role="region" aria-label="Held-out calibration table" tabIndex={0}>
              <table>
                <thead>
                  <tr><th scope="col">Delay bin (days)</th><th scope="col">Trials</th><th scope="col">Observed</th><th scope="col">Exponential</th><th scope="col">Power law</th></tr>
                </thead>
                <tbody>
                  {cal.bins.map((b) => (
                    <tr key={b.bin}>
                      <th scope="row">{b.bin}</th>
                      <td>{b.trials.toLocaleString("en-US")}</td>
                      <td>{b.display_observed}</td>
                      <td>{b.display_exponential}</td>
                      <td>{b.display_power}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Figure>
        </div>
      </section>

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          Every experiment and test is listed with the same weight, including the negative held-out test and the
          contradictory exploratory result. Numbers are read from <code>results.json</code>, exported from the committed
          results. They are printed exactly as in the manuscript and reports and are separate from anything the
          playground produces. Engine revisions of the results: {r.code_revision}.
        </p>
        {r.experiments.map((e) => (
          <ExperimentPanel key={e.id} e={e} r={r} />
        ))}
      </section>
    </>
  );
}

function ExperimentPanel({ e, r }: { e: Experiment; r: Results }) {
  return (
    <article className="sheet" aria-labelledby={`h-${e.id}`}>
      <p className={`label ${LABEL_CLASS(e.label)}`}>{e.label}</p>
      <h3 id={`h-${e.id}`}>{e.id}: {e.title}</h3>
      <p><span className="badge">{e.status}</span></p>
      <p className="verdict"><strong>Verdict under the frozen rule:</strong> {e.verdict}</p>
      {e.estimates.length > 0 && (
        <div id={`tbl-${e.id}`} className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">Quantity</th>
                <th scope="col">Estimate</th>
                <th scope="col">Interval</th>
              </tr>
            </thead>
            <tbody>
              {e.estimates.map((x) => (
                <tr key={x.label}>
                  <th scope="row">{x.label}</th>
                  <td>{fmtEstimate(x)}</td>
                  <td>{fmtInterval(x)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {e.id === "EXP-002" && <GridView r={r} />}
      {e.id === "EXP-003" && <EffectsView r={r} />}
      {e.notes.map((n, i) => (
        <p key={i} className="note">{n}</p>
      ))}
      <p className="meta">
        Report <code>{e.report_path}</code>; claims {e.claim_ids.join(", ")}; engine revision <code>{e.code_revision.slice(0, 7)}</code>.
      </p>
    </article>
  );
}

function GridView({ r }: { r: Results }) {
  const g = r.exp002_grid;
  const h0s = [...new Set(g.cells.map((c) => c.h0_days))];
  return (
    <Figure id="f-grid" title={`EXP-002: ${g.contrast} in each of the ${g.cells.length} cells, with 95% intervals`}
      desc={<>One row per cell (h0 in days, gain coefficient a, availability q); the dot is the mean paired difference and the horizontal bar its 95% interval (often narrower than the dot). The shaded band is the ±{g.sesoi} smallest effect size of interest. Every cell lies well below the band.</>}>
      {h0s.map((h0) => (
        <div key={h0}>
          <p className="facet">h0 = {h0} days</p>
          <ForestChart sesoi={g.sesoi} xLabel="A2 - A1 in R30" ariaLabel={`EXP-002 cells at h0 = ${h0} days`}
            rows={g.cells.filter((c) => c.h0_days === h0).map((c) => ({
              key: c.cell_id, label: `a = ${c.a}, q = ${c.q}`, est: c.estimate, lo: c.ci_low, hi: c.ci_high,
              text: `${c.display} ${c.interval_display}, ${c.classification}`,
            }))} />
        </div>
      ))}
      <Disclosure summary="All 27 cells as a table">
        <div id="tbl-grid" className="table-scroll" role="region" aria-label="EXP-002 cells table" tabIndex={0}>
          <table>
            <thead><tr><th scope="col">h0 (days)</th><th scope="col">a</th><th scope="col">q</th><th scope="col">A2 - A1</th><th scope="col">95% CI</th><th scope="col">Class</th></tr></thead>
            <tbody>
              {g.cells.map((c) => (
                <tr key={c.cell_id}><td>{c.h0_days}</td><td>{c.a}</td><td>{c.q}</td><td>{c.display}</td><td>{c.interval_display}</td><td>{c.classification}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </Disclosure>
    </Figure>
  );
}

function EffectsView({ r }: { r: Results }) {
  const ef = r.exp003_effects;
  return (
    <Figure id="f-eff" title="EXP-003: timing, selection and their interaction, per model variant (95% intervals)"
      desc={<>For each model variant, the overall A2 - A1 gap, the selection main effects, the timing main effect and the timing by selection interaction. Selection (easiest first) carries almost the whole gap; timing and the interaction stay inside the ±{ef.sesoi} band.</>}>
      {ef.variants.map((v) => (
        <div key={v.variant}>
          <p className="facet">{v.name}</p>
          <ForestChart sesoi={ef.sesoi} xLabel="Effect on R30" ariaLabel={`EXP-003 effects, ${v.name}`}
            rows={v.effects.map((e) => ({ key: e.effect, label: e.effect, est: e.estimate, lo: e.ci_low, hi: e.ci_high,
              text: `${e.display} ${e.interval_display}, ${e.classification}` }))} />
        </div>
      ))}
      <Disclosure summary="All effects as a table">
        <div id="tbl-eff" className="table-scroll" role="region" aria-label="EXP-003 effects table" tabIndex={0}>
          <table>
            <thead><tr><th scope="col">Variant</th><th scope="col">Effect</th><th scope="col">Estimate</th><th scope="col">95% CI</th><th scope="col">Class</th></tr></thead>
            <tbody>
              {ef.variants.flatMap((v) => v.effects.map((e) => (
                <tr key={v.variant + e.effect}><td>{v.name}</td><td>{e.effect}</td><td>{e.display}</td><td>{e.interval_display}</td><td>{e.classification}</td></tr>
              )))}
            </tbody>
          </table>
        </div>
      </Disclosure>
    </Figure>
  );
}

function Background({ r }: { r: Results }) {
  return (
    <>
      <section id="assumptions" aria-labelledby="h-assumptions">
        <p className="label label-assumption">Assumption values: model inputs, not results</p>
        <h2 id="h-assumptions">Assumptions</h2>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" className="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <h3>Method</h3>
        <ul>
          <li>The unit is one synthetic learner. Every policy runs on every learner with common random numbers, so contrasts are within-learner paired differences.</li>
          <li>The protocol and the three experiment protocols were frozen by the owner before any confirmatory run; each experiment then ran once in full, with no failed simulation.</li>
          <li>Intervals are stratified percentile bootstrap intervals over learners; the frozen decision rule compares them with the smallest effect size of interest.</li>
          <li>Exploratory work (the pre-freeze floor regime and the sensitivity checks) used development seeds only and changes no confirmatory verdict.</li>
        </ul>
        <h3>Limitations (as in manuscript section 7)</h3>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}

/** A details element whose content is mounted only while open, so closed content holds no tab stop. */
function Disclosure({ summary, children }: { summary: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <details open={open} onToggle={(e) => setOpen((e.currentTarget as HTMLDetailsElement).open)}>
      <summary>{summary}</summary>
      {open && children}
    </details>
  );
}

/** Segmented control: buttons with aria-pressed; the thumb slides to the chosen option. */
function Segmented({ label, options, value, onChange }: { label: string; options: [string, string][]; value: string; onChange: (v: string) => void }) {
  const at = Math.max(0, options.findIndex(([k]) => k === value));
  return (
    <div className="seg" role="group" aria-label={label} style={{ ["--n" as string]: options.length, ["--at" as string]: at }}>
      <span className="thumb" aria-hidden="true" />
      {options.map(([k, text]) => (
        <button key={k} type="button" aria-pressed={k === value} onClick={() => onChange(k)}>{text}</button>
      ))}
    </div>
  );
}
