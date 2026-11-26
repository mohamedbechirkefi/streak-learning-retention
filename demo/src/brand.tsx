// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Brand pieces of the page: the hero grade book (an illustration, never data) and the
// report card, which draws the published EXP-001 arm profiles as a grade book.
import type { CSSProperties } from "react";
import type { ArmProfile } from "./results";
import { useReveal } from "./charts";

const DAYS = 28;
const ITEMS = 8;
const PRACTISED = 3; // rows that receive the ticks in the sketch
const P = 24; // cell pitch in viewBox units
const C = 20; // cell size
const W = DAYS * P - (P - C) + 34; // room on the right for the red-pen bracket

const v = (o: Record<string, number>) => o as unknown as CSSProperties;

/** Hero: a habit calendar that fills, over a grade book whose unreviewed rows fade. */
export function HeroBook() {
  const gbH = ITEMS * P - (P - C);
  const fadeTop = PRACTISED * P - 2;
  return (
    <figure className="book" aria-labelledby="hb-cap">
      <p className="book-tag">Illustration, not study data</p>
      <p className="book-label">Habit calendar <span>one square per day practised</span></p>
      <svg viewBox={`0 0 ${W} ${C}`} role="img" aria-label="Sketch of a habit calendar in which every one of 28 days is filled">
        {Array.from({ length: DAYS }, (_, d) => (
          <g key={d}>
            <rect className="hb-slot" x={d * P} y={0} width={C} height={C} rx={4} />
            <rect className="hb-day" style={v({ "--i": d })} x={d * P} y={0} width={C} height={C} rx={4} />
          </g>
        ))}
      </svg>
      <p className="book-label" style={{ marginTop: "1.1rem" }}>Grade book <span>one row per item, a tick when reviewed</span></p>
      <svg viewBox={`0 0 ${W} ${gbH}`} role="img"
        aria-label="Sketch of a grade book: the daily ticks land on the same three easy items, and the five items never reviewed fade">
        {Array.from({ length: ITEMS }, (_, r) => {
          const row = <rect className="hb-row" x={0} y={r * P} width={DAYS * P - (P - C)} height={C} rx={4} />;
          return r < PRACTISED ? (
            <g key={r}>{row}</g>
          ) : (
            <g key={r} className="hb-fade" style={v({ "--r": r - PRACTISED })}>{row}</g>
          );
        })}
        {Array.from({ length: DAYS }, (_, d) => {
          const x = d * P, y = (d % PRACTISED) * P;
          return <path key={d} className="hb-tick" style={v({ "--i": d })} d={`M${x + 5} ${y + 10.5}l3.8 4l6.4 -8`} />;
        })}
        <path className="hb-pen" d={`M${W - 26} ${fadeTop + 4}h10v${gbH - fadeTop - 6}h-10`} />
      </svg>
      <figcaption id="hb-cap">
        The calendar is full; the grade book is not. A streak counts days, while recall depends on which items are
        practised. <span style={{ color: "var(--redpen)", fontStyle: "italic", fontWeight: 600 }}>Bracketed: items never reviewed, fading.</span>
      </figcaption>
    </figure>
  );
}

/** Key result: the four EXP-001 policies as a report card, attendance next to the grade. */
export function ReportCard({ arms }: { arms: ArmProfile[] }) {
  const [ref, reveal] = useReveal<HTMLDivElement>();
  const pct = (x: number) => `${Math.max(0, Math.min(100, x * 100)).toFixed(2)}%`;
  return (
    <div ref={ref} className={`report${reveal}`}>
      <div className="table-scroll" role="region" aria-label="Report card: days practised, longest streak and R30 per policy" tabIndex={0}>
        <table id="tbl-report">
          <thead>
            <tr>
              <th scope="col">Policy</th>
              <th scope="col">Days practised (mean, of 56)</th>
              <th scope="col">Longest streak (mean days)</th>
              <th scope="col">R30, recall 30 days after practice</th>
            </tr>
          </thead>
          <tbody>
            {arms.map((a, k) => (
              <tr key={a.arm} className={a.arm === "A2" ? "hl" : undefined}>
                <th scope="row">{a.name}</th>
                <td data-h="Days practised (mean, of 56)">
                  <span className="num">{a.active_days.display}</span>
                  <div className="days" aria-hidden="true">
                    {[0, 1].map((row) => (
                      <div key={row}><i /><b style={{ ...v({ "--k": k }), ["--f" as string]: pct(Math.min(1, Math.max(0, (a.active_days.mean - 28 * row) / 28))) }} /></div>
                    ))}
                  </div>
                </td>
                <td data-h="Longest streak (mean days)"><span className="num">{a.longest_streak.display}</span></td>
                <td data-h="R30, recall 30 days after practice">
                  <span className="num">{a.r30.display}</span>
                  <span className="sub">{a.r30.interval_display}</span>
                  <div className="grade" aria-hidden="true">
                    <b className={a.arm.toLowerCase()} style={{ ...v({ "--k": k }), ["--f" as string]: pct(a.r30.mean) }} />
                    <s style={{ left: pct(a.r30.ci_low) }} />
                    <s style={{ left: pct(a.r30.ci_high) }} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="meta report-note">
        Means over 1,000 synthetic learners per policy; practice minutes are matched across the practising policies.
        Day squares: the mean number of practice days out of 56, in two rows of 28. Grade bars: R30 on a scale from 0
        to 1, with the 95% interval marked.
      </p>
    </div>
  );
}
