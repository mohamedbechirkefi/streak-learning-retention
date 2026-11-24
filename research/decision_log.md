<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Decision log (append-only)

Format: D-NNN, date, decision, rationale, alternatives, decided by, consequences.

## D-001 (2026-11-24): Repository licence is the owner's protective non-commercial licence

- **Decision.** All original material is licensed under the STREAK Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-STREAK-NC-Research-1.0`), with a CLA for contributions.
- **Context.** Master prompt section 2 asks for an "owner-approved permissive code license". On 2026-11-24 the owner chose this protective licence instead, for their own protection.
- **Decided by.** The owner. The licence package (LICENSE, NOTICE.md, LICENSE_HISTORY.md, CLA.md, CONTRIBUTING.md, .github/) was committed before this session and is not modified by the AI.
- **Consequences.** The project is source-available, not OSI open source. Data and dependency licences are recorded separately (data/manifest.json, uv.lock). Some venues or archives may expect an OSI licence; this is a known trade-off for the owner.

## D-002 (2026-11-24): Zero-cost publication toolchain without TeX

- **Decision.** PDFs are produced as pandoc (3.6.3) Markdown to Typst, compiled with the `typst` Python package (0.15.0). `research/paper/manuscript.tex` is generated from Markdown with pandoc and not compiled locally.
- **Rationale.** No TeX distribution is installed (tex, pdflatex, xelatex, latexmk not found). Installing one is not required and the master prompt forbids paid tools; Typst is free and already available.
- **Alternatives.** Installing TeX Live (large, not needed); HTML-to-PDF via a browser (less reproducible).
- **Decided by.** AI proposal following the owner's M0 brief. Reversible.

## D-003 (2026-11-24): Synthetic data only for the confirmatory design

- **Decision.** All registered experiments use synthetic learners. No external dataset is downloaded or required.
- **Rationale.** The question concerns a learning model; candidate public datasets have unverified or gated licences (Duolingo Dataverse record unreachable, HTTP 503; anki-revlogs-10k gated with a custom licence).
- **Decided by.** AI proposal, pending owner confirmation (owner decision OD-3 in roadmap.md).

## D-004 (2026-11-24): Draft protocol choices (proposal, not frozen)

- **Decision (proposal).** Primary baseline A1 Fixed (3 sessions per week, round-robin); primary metric R30 (mean expected recall 30 days after practice ends); primary contrast A2 Streak minus A1 Fixed, two-sided, SESOI 0.02; within-learner paired design with common random numbers; 5 master seeds × 200 learners; stratified bootstrap. Invalidating sensitivity: flat-gain update rule (EXP-003).
- **Rationale.** See research/protocol.md sections 4 to 9. A1 is the simplest comparator (no learner model, no adaptivity). R30 measures retention after a held-out delay, the construct opposed to activity.
- **Status.** Draft. Freezing is the owner's decision (G-FREEZE).

## D-005 (2026-11-24): Dependencies limited to releases at least two weeks old

- **Decision.** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"` so that the lockfile resolves only package versions released on or before 2026-11-10.
- **Rationale.** Owner brief requires versions released at least two weeks before 2026-11-24; minimises supply-chain risk of very fresh releases.
- **Decided by.** AI, following the owner's brief.

## D-006 (2026-11-24): M2 package and tooling layout

- **Decision.** The engine is the Python package `streak` (`src/streak`, built with the `uv_build` backend, editable install by `uv sync`). Modules are separated by role: `params` (validated parameters, arm definitions), `memory` (forgetting curves, update rules), `population` (synthetic learner generation, the only "ingestion"), `simulate` (one learner-arm), `metrics` (per learner-arm metrics), `stats` (paired analysis), `runner` (config to results, gate check), `schema` and `schemas/` (versioned JSON schemas `streak.config/1.0`, `streak.result/1.0`, `streak.manifest/1.0`), `manifest` (environment capture), `report` (tables, figures, Markdown, PDF) and `cli` (`smoke`, `run`, `report`, `test`).
- **Rationale.** Master prompt sections 4 and 11.6 (M2). No new runtime dependency: the schema validator implements the JSON Schema keywords the schema files use, and figures are written as plain SVG, so neither `jsonschema` nor `matplotlib` is needed. The lockfile only changed the project entry (virtual to editable, version 0.2.0); `uv_build` is a build-time requirement constrained to `>=0.9.5,<0.10` (uv 0.9.5 was released on 2025-10-21, well before the D-005 cut-off).
- **Decided by.** AI, within the M2 brief. Reversible.

## D-007 (2026-11-24): Implementation readings of points the draft protocol leaves open

These are the AI's readings, implemented in engine 1.0.x and listed for owner confirmation before the freeze. None changes a metric, arm or hypothesis.

1. **Scheduler belief in non-default cells.** The belief always uses the exponential form and the difficulty-dependent gain, with the cell's population values of h0, g_min, a, b and h_min (θ = 1, u = 1). In EXP-002 the scheduler therefore knows the cell's population parameters but not the individual learner or item. In EXP-003 the belief stays exponential and difficulty-dependent while the true model varies (as P§2 and EXP-003 §6 state).
2. **Common random numbers for outcomes.** Each learner has a fixed (T + 1) × K matrix of uniforms; a review of item i on day d succeeds iff the uniform is below the true recall probability. The same (day, item) review therefore has the same outcome draw in every arm, cell and model variant. Availability uses one uniform per day (available iff below q), so a day available at q = 0.7 is also available at q = 0.85.
3. **Within-day order.** All of a day's reviews happen at t = d; the selection is made from the beliefs at the start of the day; at most min(daily cap, K) reviews per day.
4. **Belief update** uses the observed outcome of the review and the belief's own estimate of p at review time.
5. **Final streak** is the run of consecutive active days ending on day T (0 if day T is inactive). **Weakest-decile R30** is the mean R30 of the round(0.1 K) items with the lowest R30.
6. **Holm-adjusted intervals (P§6).** Implemented as Holm-adjusted two-sided bootstrap p-values for the secondary contrasts within each cell, reported next to unadjusted 95% and 90% intervals. See amendment proposal AP-5.
7. **Confirmatory gate.** `streak.cli run` treats a config labelled `confirmatory` as runnable only if the experiment's row in `research/experiment_registry.csv` carries a 64-hex SHA-256 equal to the hash of the protocol file on disk and `research/protocol.md` no longer contains "NOT FROZEN". Exploratory configs may only use seeds 9001 to 9999; confirmatory configs may not use them.

## D-008 (2026-11-24): Integer-valued parameters coerced to float (engine 1.0.1)

- **Finding.** The first exploratory EXP-002 smoke run (on commit f914ddd) recorded 5,380 failed learner-arms of 10,800, all in the 18 cells with h0 = 1 or 2: the JSON grid gives these as integers, `np.full(K, h0)` then created an integer belief array and half-life updates were truncated to 0 ("half_life must be positive"). EXP-001 configs (h0 = 1.0) were not affected. The failures were recorded per learner-arm as designed, not dropped.
- **Decision.** `ModelParams` coerces every real-valued field to float; the belief array is explicitly float. A regression test compares integer-valued and float-valued parameters and fails on the previous revision. Engine version 1.0.0 to 1.0.1. The faulty outputs were discarded (they were exploratory and regenerated) and are described here and in the journal.
- **Decided by.** AI (bug fix; no scientific choice involved).

## D-009 (2026-11-24): Storage of exploratory smoke outputs

- **Decision.** Exploratory outputs live under `results/exploratory/<ID>/` (run manifest, generated report, tables and figures, committed). Raw result files larger than about 1 MB go to `results/raw/exploratory/<ID>/` (git-ignored, regenerated by the commands in `results/exploratory/README.md`). The raw result of the 400-learner-arm smoke run (`SMOKE-EXP-001`) is small and committed as a fixture.
- **Rationale.** Brief: exploratory outputs clearly separate from any confirmatory results; large generated files stay out of git. Exploratory IDs use the `SMOKE-` prefix and never an EXP id.

## D-010 (2026-11-24): Run manifests ignore untracked files when recording git_dirty

- **Decision.** `git_dirty` is computed with `git status --porcelain --untracked-files=no`. Before this change, outputs written by one smoke run marked the manifests of later runs dirty although the source revision was clean.

## D-011 (2026-11-24): Duolingo traces adopted after a clean licence recheck (supersedes D-003 for h0)

- **Decision.** The Duolingo half-life regression traces (Settles and Meeder 2016; Harvard Dataverse doi:10.7910/DVN/N8XJME) are adopted to calibrate the median initial half-life h0 and for a preregistered second test of the forgetting model on held-out users (protocol section 14). Everything else stays synthetic.
- **Licence check.** On 2026-11-24 the Dataverse dataset API (`https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/N8XJME`, the same record as the dataset page `https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/N8XJME`) answered (at M0 it returned HTTP 503). Its `termsOfUse` field reads: "This work is released under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)." Version 1.0, released 2017-12-14; one file, `settles.acl16.learning_traces.13m.csv.gz`, 379,004,009 bytes, MD5 0a1cae5eb7ad4b0bd9c0de91d74fcced, not restricted. CC BY-NC 4.0 clearly permits non-commercial research use with attribution, which is the owner's condition (approvals 2026-11-24b, section 1: "Adopt only if a licence recheck is clean"). Blocker B-1 is resolved.
- **Handling.** Above 20 MB and holding pseudonymous user ids at row level: downloaded by `scripts/download_duolingo.py` into `data/raw/` (git-ignored), never committed, nor is the processed form. User ids are used only for the split hash. Attribution to Settles and Meeder (2016) and the dataset DOI is carried in `data/manifest.json` and in the manuscript.
- **Decided by.** The owner ("Approve all", 2026-11-24), conditional on this check, which the AI performed and recorded.

## D-012 (2026-11-24): Calibration method, floor check and amendments written before fitting

- **Decision.** Protocol section 14 (round-2 amendments) fixes, before any fit: the observations used (first repeats, delay 1 to 90 days), the user split (SHA-256 of user id, first byte even = fit), the estimator (marginal binomial maximum likelihood of h0 with the model's own heterogeneity σ = 0.5831 fixed, exponential form), the rounding and how the fitted value enters the configs (base h0 and the EXP-002 h0 axis {0.5, 1, 2} times the fit), a control-only floor check (A0 and A1 on smoke seeds; K ladder 100, 50 or 200, 400), the held-out second test, the threshold-based A3 (r* = 0.9), the Holm wording, and the disclosure of the A2 > A1 smoke values. The section was committed before the fit so the order is visible in git.
- **Not applied.** AP-3, AP-4 and AP-6 are not in the owner's approved list for STREAK and are left as they were.
- **Implementation.** `streak.duolingo` (pure ingestion with schema validation and counts; fit; held-out evaluation), `scripts/download_duolingo.py`, selection `due_threshold` for A3 and F-DUE (engine 1.1.0; the old `most_due` rule kept, used by no arm), optional `holm_primary_across_cells` in the analysis config (used by EXP-002).
- **Decided by.** The owner approved the amendments; the concrete method is the AI's, fixed in the protocol for the owner's review at the freeze.
