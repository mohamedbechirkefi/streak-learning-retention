// SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
// Hand-written SVG charts. Every chart draws only the data passed to it, sizes itself
// to its container (text stays at a readable pixel size on phones) and has a table or
// a plain-language description next to it.
import { useEffect, useRef, useState, type ReactNode } from "react";

export const ARM_STYLE: Record<string, { cls: string; marker: "circle" | "square" | "diamond" | "triangle"; dash?: string }> = {
  A0: { cls: "s-a0", marker: "triangle", dash: "2 4" },
  A1: { cls: "s-a1", marker: "circle" },
  A2: { cls: "s-a2", marker: "square", dash: "8 4" },
  A3: { cls: "s-a3", marker: "diamond" },
};

export function useWidth<T extends HTMLElement>(fallback = 640): [React.RefObject<T | null>, number] {
  const ref = useRef<T | null>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => setW(Math.max(260, Math.round(el.getBoundingClientRect().width)));
    update();
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w];
}

export function Marker({ kind, x, y, r = 5, cls }: { kind: string; x: number; y: number; r?: number; cls: string }) {
  const c = `mark ${cls}`;
  if (kind === "square") return <rect className={c} x={x - r} y={y - r} width={2 * r} height={2 * r} rx={1.5} />;
  if (kind === "diamond") return <path className={c} d={`M${x} ${y - r * 1.3}L${x + r * 1.3} ${y}L${x} ${y + r * 1.3}L${x - r * 1.3} ${y}Z`} />;
  if (kind === "triangle") return <path className={c} d={`M${x} ${y - r * 1.2}L${x + r * 1.2} ${y + r}L${x - r * 1.2} ${y + r}Z`} />;
  return <circle className={c} cx={x} cy={y} r={r} />;
}

export function Legend({ items }: { items: { arm: string; label: string }[] }) {
  return (
    <ul className="legend" aria-label="Legend">
      {items.map((it) => (
        <li key={it.arm}>
          <svg width="28" height="14" aria-hidden="true">
            <line x1="1" y1="7" x2="27" y2="7" className={`line ${ARM_STYLE[it.arm].cls}`} strokeDasharray={ARM_STYLE[it.arm].dash} />
            <Marker kind={ARM_STYLE[it.arm].marker} x={14} y={7} r={4} cls={ARM_STYLE[it.arm].cls} />
          </svg>
          {it.label}
        </li>
      ))}
    </ul>
  );
}

/** Round-step ticks inside [lo, hi] with at most about n intervals, and their labels. */
function niceTicks(lo: number, hi: number, n: number): { v: number; t: string }[] {
  const steps = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1];
  const step = steps.find((s) => (hi - lo) / s <= n) ?? 1;
  const dec = step >= 1 ? 0 : step >= 0.1 ? 1 : 2;
  const out: { v: number; t: string }[] = [];
  for (let k = Math.ceil(lo / step - 1e-9); k * step <= hi + 1e-9; k++) {
    const v = k * step;
    out.push({ v, t: (Math.abs(v) < 1e-12 ? 0 : v).toFixed(dec) });
  }
  return out;
}

function ticks(lo: number, hi: number, n: number): number[] {
  const step = (hi - lo) / n;
  return Array.from({ length: n + 1 }, (_, i) => lo + i * step);
}

/**
 * Reveal once when scrolled into view. Only elements that start below the fold are hidden
 * first, and never under reduced motion or without IntersectionObserver, so content is
 * always visible when the effect cannot run.
 */
export function useReveal<T extends HTMLElement>(): [React.RefObject<T | null>, string] {
  const ref = useRef<T | null>(null);
  const [cls, setCls] = useState("");
  useEffect(() => {
    const el = ref.current;
    if (!el || typeof IntersectionObserver === "undefined") return;
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    if (el.getBoundingClientRect().top < window.innerHeight) return;
    setCls(" reveal");
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        setCls(" reveal in");
        io.disconnect();
      }
    }, { rootMargin: "0px 0px -8% 0px" });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return [ref, cls];
}

export function Figure({ id, title, desc, children, wide }: { id: string; title: string; desc: ReactNode; children: ReactNode; wide?: boolean }) {
  const [ref, reveal] = useReveal<HTMLElement>();
  return (
    <figure ref={ref} className={`chart${wide ? " wide" : ""}${reveal}`} aria-labelledby={`${id}-t`} aria-describedby={`${id}-d`}>
      <figcaption id={`${id}-t`} className="chart-title">{title}</figcaption>
      {children}
      <p id={`${id}-d`} className="chart-desc">{desc}</p>
    </figure>
  );
}

// ---------------- Streak versus recall (EXP-001, published) ----------------

export interface SvrPoint { arm: string; label: string; x: number; y: number; lo: number; hi: number; xText: string; yText: string }

export function StreakRecallChart({ points, xLabel, xMax }: { points: SvrPoint[]; xLabel: string; xMax: number }) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const h = Math.min(380, Math.max(280, w * 0.6));
  const m = { l: 52, r: 16, t: 14, b: 46 };
  const X = (v: number) => m.l + (v / xMax) * (w - m.l - m.r);
  const Y = (v: number) => m.t + (1 - v) * (h - m.t - m.b);
  // Direct labels: place to the right of the mark unless near the right edge.
  return (
    <div ref={ref} className="svg-wrap">
      <svg width={w} height={h} role="img" aria-label={`Scatter of ${xLabel.toLowerCase()} against mean R30 per policy`}>
        {ticks(0, 1, 5).map((t) => (
          <g key={t}>
            <line className="grid" x1={m.l} x2={w - m.r} y1={Y(t)} y2={Y(t)} />
            <text className="tick" x={m.l - 8} y={Y(t) + 4} textAnchor="end">{t.toFixed(1)}</text>
          </g>
        ))}
        {ticks(0, xMax, xMax >= 50 ? 4 : 4).map((t) => (
          <text key={t} className="tick" x={X(t)} y={h - m.b + 18} textAnchor="middle">{Math.round(t)}</text>
        ))}
        <line className="axis" x1={m.l} x2={w - m.r} y1={h - m.b} y2={h - m.b} />
        <text className="axis-label" x={(m.l + w - m.r) / 2} y={h - 6} textAnchor="middle">{xLabel}</text>
        <text className="axis-label" transform={`translate(14 ${(m.t + h - m.b) / 2}) rotate(-90)`} textAnchor="middle">Mean R30 (proportion recalled)</text>
        {points.map((p) => {
          const s = ARM_STYLE[p.arm];
          const right = X(p.x) < w - 150;
          const dy = p.arm === "A3" ? -12 : p.arm === "A1" ? 18 : p.arm === "A2" ? -12 : 18;
          return (
            <g key={p.arm}>
              <title>{`${p.label}: ${xLabel.toLowerCase()} ${p.xText}, R30 ${p.yText}`}</title>
              <line className={`errbar ${s.cls}`} x1={X(p.x)} x2={X(p.x)} y1={Y(p.hi)} y2={Y(p.lo)} />
              <Marker kind={s.marker} x={X(p.x)} y={Y(p.y)} r={6} cls={s.cls} />
              <text className="dlabel" x={X(p.x) + (right ? 12 : -12)} y={Y(p.y) + dy} textAnchor={right ? "start" : "end"}>
                {p.label}: {p.yText}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// ---------------- Line chart over days (memory curves) ----------------

export interface Series { arm: string; label: string; pts: { x: number; y: number; lo?: number | null; hi?: number | null }[] }

export function LineChart({ series, xLabel, xMin, xMax, yLabel, marks, vline, ariaLabel, yMin = 0 }: {
  series: Series[]; xLabel: string; xMin: number; xMax: number; yLabel: string; marks?: boolean;
  vline?: { x: number; label: string }; ariaLabel: string; yMin?: number;
}) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const h = Math.min(340, Math.max(250, w * 0.55));
  const m = { l: 52, r: 16, t: 14, b: 46 };
  const X = (v: number) => m.l + ((v - xMin) / (xMax - xMin)) * (w - m.l - m.r);
  const Y = (v: number) => m.t + (1 - (v - yMin) / (1 - yMin)) * (h - m.t - m.b);
  return (
    <div ref={ref} className="svg-wrap">
      <svg width={w} height={h} role="img" aria-label={ariaLabel}>
        {ticks(yMin, 1, 5).map((t) => (
          <g key={t}>
            <line className="grid" x1={m.l} x2={w - m.r} y1={Y(t)} y2={Y(t)} />
            <text className="tick" x={m.l - 8} y={Y(t) + 4} textAnchor="end">{t.toFixed(yMin > 0 ? 2 : 1)}</text>
          </g>
        ))}
        {ticks(xMin, xMax, w < 420 ? 3 : 6).map((t) => (
          <text key={t} className="tick" x={X(t)} y={h - m.b + 18} textAnchor="middle">{Math.round(t)}</text>
        ))}
        <line className="axis" x1={m.l} x2={w - m.r} y1={h - m.b} y2={h - m.b} />
        {vline && (
          <g>
            <line className="vline" x1={X(vline.x)} x2={X(vline.x)} y1={m.t} y2={h - m.b} />
            <text className="tick" x={X(vline.x) + 4} y={m.t + 12}>{vline.label}</text>
          </g>
        )}
        <text className="axis-label" x={(m.l + w - m.r) / 2} y={h - 6} textAnchor="middle">{xLabel}</text>
        <text className="axis-label" transform={`translate(14 ${(m.t + h - m.b) / 2}) rotate(-90)`} textAnchor="middle">{yLabel}</text>
        {series.map((s) => {
          const st = ARM_STYLE[s.arm];
          const d = s.pts.map((p, i) => `${i ? "L" : "M"}${X(p.x).toFixed(1)} ${Y(p.y).toFixed(1)}`).join("");
          return (
            <g key={s.arm}>
              <path className={`line ${st.cls}`} d={d} strokeDasharray={st.dash} />
              {s.pts.map((p) =>
                p.lo != null && p.hi != null ? (
                  <line key={`e${p.x}`} className={`errbar ${st.cls}`} x1={X(p.x)} x2={X(p.x)} y1={Y(p.hi)} y2={Y(p.lo)} />
                ) : null,
              )}
              {marks && s.pts.map((p) => (
                <g key={p.x}>
                  <title>{`${s.label}, ${p.x} days: ${p.y.toFixed(4)}`}</title>
                  <Marker kind={st.marker} x={X(p.x)} y={Y(p.y)} r={4.5} cls={st.cls} />
                </g>
              ))}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// ---------------- Dot-and-interval (forest) chart ----------------

export interface ForestRow { key: string; label: string; est: number; lo: number; hi: number; text: string; group?: string }

export function ForestChart({ rows, sesoi, xLabel, ariaLabel }: { rows: ForestRow[]; sesoi: number; xLabel: string; ariaLabel: string }) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const narrow = w < 520;
  const labelW = narrow ? 0 : Math.min(260, w * 0.38);
  const rowH = narrow ? 40 : 24;
  const m = { l: 10 + labelW, r: 14, t: 26, b: 44 };
  const lo = Math.min(-sesoi * 2, ...rows.map((r) => r.lo));
  const hi = Math.max(sesoi * 2, ...rows.map((r) => r.hi));
  const pad = (hi - lo) * 0.05;
  const x0 = lo - pad, x1 = hi + pad;
  const h = m.t + rows.length * rowH + m.b;
  const X = (v: number) => m.l + ((v - x0) / (x1 - x0)) * (w - m.l - m.r);
  const tickVals = niceTicks(x0, x1, narrow ? 4 : 8);
  return (
    <div ref={ref} className="svg-wrap">
      <svg width={w} height={h} role="img" aria-label={ariaLabel}>
        <rect className="sesoi" x={X(-sesoi)} y={m.t - 6} width={X(sesoi) - X(-sesoi)} height={rows.length * rowH + 6} />
        <text className="tick" x={X(sesoi)} y={m.t - 10} textAnchor="end">SESOI band ±{sesoi}</text>
        <line className="zero" x1={X(0)} x2={X(0)} y1={m.t - 6} y2={m.t + rows.length * rowH} />
        {tickVals.map((t) => (
          <text key={t.t} className="tick" x={X(t.v)} y={h - m.b + 18} textAnchor="middle">{t.t}</text>
        ))}
        <line className="axis" x1={m.l} x2={w - m.r} y1={m.t + rows.length * rowH} y2={m.t + rows.length * rowH} />
        <text className="axis-label" x={(m.l + w - m.r) / 2} y={h - 6} textAnchor="middle">{xLabel}</text>
        {rows.map((r, i) => {
          const yc = m.t + i * rowH + (narrow ? rowH - 12 : rowH / 2);
          return (
            <g key={r.key}>
              <title>{`${r.label}: ${r.text}`}</title>
              {narrow ? (
                <text className="tick" x={m.l} y={yc - 12}>{r.label}</text>
              ) : (
                <text className="tick" x={m.l - 8} y={yc + 4} textAnchor="end">{r.label}</text>
              )}
              <line className="errbar s-est" x1={X(r.lo)} x2={X(r.hi)} y1={yc} y2={yc} />
              <circle className="mark s-est" cx={X(r.est)} cy={yc} r={4.5} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// ---------------- Learning timeline (sandbox) ----------------

export function Timeline({ rows, horizon }: { rows: { arm: string; label: string; spent: number[]; available: boolean[] }[]; horizon: number }) {
  const [ref, w] = useWidth<HTMLDivElement>();
  const labelW = w < 420 ? 74 : 110;
  const cell = (w - labelW - 8) / horizon;
  const rowH = 30;
  const h = rows.length * rowH + 34;
  const maxSlots = Math.max(1, ...rows.flatMap((r) => r.spent));
  return (
    <div ref={ref} className="svg-wrap">
      <svg width={w} height={h} role="img" aria-label="Day-by-day practice of the first synthetic learner under each policy">
        {rows.map((r, i) => (
          <g key={r.arm} transform={`translate(0 ${i * rowH})`}>
            <text className="tick" x={0} y={rowH / 2 + 4}>{r.label}</text>
            {Array.from({ length: horizon }, (_, k) => {
              const d = k + 1;
              const s = r.spent[d] ?? 0;
              const x = labelW + k * cell;
              const hh = s > 0 ? Math.max(3, ((rowH - 8) * s) / maxSlots) : 0;
              return (
                <g key={d}>
                  <title>{`Day ${d}: ${r.available[d] ? (s > 0 ? `${s} reviews` : "available, no practice") : "not available"}`}</title>
                  {!r.available[d] && <rect className="unavail" x={x + 0.5} y={rowH - 10} width={Math.max(1, cell - 1)} height={4} />}
                  {s > 0 && <rect style={{ "--i": k } as React.CSSProperties} className={`bar ${ARM_STYLE[r.arm].cls}`} x={x + 0.5} y={rowH - 4 - hh} width={Math.max(1, cell - 1)} height={hh} rx={1} />}
                </g>
              );
            })}
          </g>
        ))}
        {[1, 14, 28, 42, horizon].map((d) => (
          <text key={d} className="tick" x={labelW + (d - 0.5) * cell} y={h - 6} textAnchor="middle">{d}</text>
        ))}
      </svg>
    </div>
  );
}
