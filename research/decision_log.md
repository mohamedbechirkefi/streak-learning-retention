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
