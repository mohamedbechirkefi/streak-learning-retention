<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Feasibility audit (M0, 2026-11-24)

Status: complete for M0. All values below were confirmed by commands run on 2026-11-24; the commands and outputs are recorded in `progress.md`.

## 1. Hardware

| Item | Value | Confirming command |
|---|---|---|
| CPU | Apple M1 Pro, 10 cores | `sysctl -n machdep.cpu.brand_string hw.ncpu` |
| Memory | 17179869184 bytes (16 GiB) | `sysctl -n hw.memsize` |
| OS | macOS 15.3.1 (build 24D70) | `sw_vers` |
| Free disk | 129 GiB available on the data volume | `df -h` |

## 2. Tools

| Tool | Version | Location | Use |
|---|---|---|---|
| Python | 3.12.1 | `/usr/local/bin/python3` | simulation, analysis, tests |
| uv | 0.9.5 | `../.tools/py/bin/uv` (relative to the repository) | lockfile, environment |
| typst (Python package) | 0.15.0 | `../.tools/py/bin/python` | PDF compilation |
| pypdf | 6.20.0 | same | PDF inspection |
| pillow | 11.3.0 | same | figure and page inspection |
| pandoc | 3.6.3 | `../.tools/pandoc` | Markdown to Typst and LaTeX |
| Node | v22.23.3 | `../../helix/.tools/node/bin` | static demo build (read-only use) |
| git | 2.42.1 | system | version control (local only) |
| TeX (tex, pdflatex, xelatex, latexmk) | not found | none | not available |

**Zero-cost publication toolchain (decision D-002).** There is no TeX distribution. Every PDF (manuscript and per-experiment reports) is planned as pandoc Markdown to Typst, then compiled with the `typst` Python package. `research/paper/manuscript.tex` is generated from Markdown with pandoc for venue compatibility but is not compiled locally. An exploratory smoke check of this toolchain on the manuscript skeleton was run in M0 (see `progress.md`); its PDF was written outside the repository and is not a deliverable.

## 3. Compute budget

The simulation is small: per learner, about 100 items over a 56-day horizon with at most a few hundred review events. Planning estimate (labelled as such, to be measured in the M3 smoke run): the full matrix of all three experiments is below 200,000 learner-arm simulations, which should run in minutes on one core with NumPy. No GPU, cloud or paid compute is needed. Runtime and peak memory will be recorded per run.

## 4. Time budget

Five focused development days (planning estimate). Proposed split: M0+M1 0.75 day, M2 1.5 days, M3 0.75 day, M4 0.75 day, M5 0.75 day, M6 0.5 day. If the target is threatened, cut in this order: demo polish, EXP-003 power-law variant, EXP-002 grid size. Never cut controls, reporting or provenance.

## 5. Sources and data

See `research/literature_review.md` (sources actually opened, with access dates) and `data/manifest.json`. The confirmatory design uses **synthetic data only**; no external dataset is needed to answer the registered question. Public learning-trace datasets were audited only as optional calibration references, and none is downloaded in M0.

| Candidate | Licence status (verified 2026-11-24) | Redistribution | Decision |
|---|---|---|---|
| Duolingo half-life regression traces, Harvard Dataverse doi:10.7910/DVN/N8XJME | Code repository is MIT (GitHub licence API). The dataset's own Dataverse licence could not be read: the Dataverse API returned HTTP 503 on 2026-11-24. **Unverified.** | Unknown | Not used. Blocker B-1 if the owner wants calibration from it. |
| open-spaced-repetition/anki-revlogs-10k (Hugging Face) | Custom "anki-revlogs-10k License" (Hugging Face metadata: `license:other`); access gated behind an account and acceptance of conditions; terms not read. **Unverified.** 15.7 GB. | Unknown, gated | Not used (requires an account; master prompt forbids requiring accounts for runtime use, and size exceeds need). |
| Murre and Dros (2015) Ebbinghaus replication, PLOS ONE | Article under CC BY 4.0 (Crossref licence metadata). Licence of any supplementary data not separately checked. | Article: yes with attribution | Optional qualitative reference for the forgetting-curve shape only. |

## 6. Scope, exclusions and fallback

- In scope: synthetic learners with forgetting, retrieval practice, daily time budgets and stochastic availability; four scheduling arms at matched practice minutes; sensitivity over forgetting parameters and model form.
- Excluded: human participants, personal data, any claim about real learning efficacy, any inference about the internals of any commercial learning product, pressure-based UX.
- Fallback if the main design proves infeasible: reduce to EXP-001 only (minimum viable release in master prompt section 10), still with all controls and reports.

## 7. Risks and blockers

| ID | Risk or blocker | Owner action needed |
|---|---|---|
| B-1 | Licence of the Duolingo dataset unverified (Dataverse 503). Only matters if calibration is wanted. | Decide whether calibration to real traces is in scope at all (recommended: no). |
| B-2 | Protocol is a draft; no confirmatory run is allowed until the owner freezes it (G-FREEZE). | Review and freeze `research/protocol.md` and EXP protocols. |
| R-1 | Main risk to validity: the result may be produced by the assumed memory-update rule (desirable-difficulty gain). EXP-003 is designed to test this. | Confirm EXP-003 stays in scope. |
| R-2 | Planning values (SESOI 0.02, standard deviation guess) are not measured; the smoke run will check them on smoke seeds only. | Confirm or change SESOI. |
| R-3 | The LICENSE is source-available non-commercial, while the master prompt asked for a permissive licence (owner decision D-001). Some venues or archives may expect an OSI licence. | Owner awareness only. |
