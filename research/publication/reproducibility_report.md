<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Reproducibility report

Status (M6, 2026-11-25): clean-clone reproduction completed with actual outputs below. Machine: Apple M1 Pro, macOS (Darwin 24.3.0); Python 3.12 via uv; Node v22.23.3. Source: local clone of commit `ff06d8d` (M5 head) into a scratch directory outside the repository; no network except the npm offline cache.

- [x] Clean clone into a separate directory.
- [x] `uv sync --frozen` from `uv.lock` succeeds.
- [x] Test suite runs; actual count and status recorded.
- [x] Smoke reproduction matches committed smoke summaries within documented tolerance (byte-identical for the M3 smoke run; see finding F-M6-1 for the M2 smoke run).
- [x] Demo builds offline.
- [x] Data manifest and links verified.
- [x] Secret and licence scan.
- [x] Manuscript and report PDFs compiled (pandoc to Typst) and pages visually inspected.

## 1. Clean clone (commit ff06d8d)

```
$ git clone -q /Users/<owner>/research/labs/streak-learning-retention <scratch>/clone
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   (installed 9 packages; second run: "Audited 9 packages")
$ .venv/bin/python -m pytest                                      225 passed in 7.10s
```

## 2. Smoke reproduction

The README of `results/exploratory/` documents `python -m streak.cli smoke` as the regeneration command of the smoke runs.

```
$ .venv/bin/python -m streak.cli smoke --config experiments/smoke-m3-exp001.json --out <scratch>/smokem3
[exploratory] SMOKE-M3-EXP-001: 400 learner-arms, 0 failed, 1.22 s, peak memory 47939584 bytes
$ shasum -a 256 <scratch>/smokem3/results.json results/exploratory/SMOKE-M3-EXP-001/results.json
edac1326fdd0bd333d183add20fb2d2267439311803fade0c05ae6ebc856ae11  (both; equal to journal J-0011)
$ cmp ...                                                          BYTE-IDENTICAL
$ .venv/bin/python scripts/validate_smoke.py <scratch>/smokem3/results.json     ALL PASS
```

Finding F-M6-1 (documentation, not a defect in any result). The default `python -m streak.cli smoke` (config `experiments/smoke-exp001.json`) gives a `results.json` (SHA-256 `e1947e99...`) that differs from the committed `results/exploratory/SMOKE-EXP-001/results.json` (`a1f8a510...`). The rows for A0, A1 and A2 are identical; the A3 rows differ (for example R30 0.1413 now against 0.0001 committed). The committed file was produced in M2 by engine revisions before the A3 operationalisation was replaced by the threshold rule (decision D-012, protocol sections 14.5 and 14.6), and the M2 file is kept as a historical exploratory artifact. The current engine reproduces the post-change smoke run (SMOKE-M3-EXP-001) byte for byte, as above. Not fixed: the M2 artifact is a dated exploratory record and must not be overwritten; the note is recorded here and in `progress.md`.

Frozen-analysis regeneration from committed raw results (EXP-001, in the clone):

```
$ .venv/bin/python scripts/analyse_confirmatory.py EXP-001
$ git status --short          M research/experiments/EXP-001/generated/frozen_analysis.json
```

Finding F-M6-2 (fixed). The only difference was the field `result_path`, which recorded the absolute path of the results file (a local home-directory path in a committed file, and a non-deterministic output across checkouts). `scripts/analyse_confirmatory.py` now writes the repository-relative path; the three `generated/frozen_analysis.json` files were regenerated and differ from the committed ones only in that field. Every table, figure and number is unchanged (checked with `git diff --stat`: one line per file).

Not reproducible from a clean clone, by design: the confirmatory runs themselves (`scripts/run_confirmatory.py`) need the git-ignored raw Duolingo file for the guard's data-hash check, and `results/confirmatory/EXP-002/results.json` is git-ignored (over 20 MB); its SHA-256 is in `results/confirmatory/EXP-002/sha256_manifest.json` and was verified against the local copy (section 5).

## 3. Demo (in the clone)

```
$ npm ci --prefer-offline                 added 53 packages in 938ms
$ npm test                                Test Files 2 passed (2); Tests 43 passed (43)
$ npm run build                           dist/index.html 0.94 kB; sandbox worker 7.41 kB; css 6.56 kB; js 259.52 kB; built in 275ms
$ node tools/a11y_check.mjs dist
PASS results render (no fail-closed panel): 6 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 24 reached of 24
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs
A11Y-CHECK PASS
```

Export determinism: `.venv/bin/python scripts/export_demo_data.py` (wrote 59605 bytes) and `scripts/export_sandbox_fixture.py` (wrote 516358 bytes) in the clone, then `git status --short`: 0 lines.

## 4. PDFs

Built with `scripts/build_pdfs.py` (pandoc 3.6.3 to Typst, `typst` Python package 0.15.0; decision D-002), which also regenerates `research/paper/manuscript.tex`. Every page was rendered to PNG at 60 ppi (figure pages also at 150 ppi) and inspected.

| PDF | Pages | Title metadata |
|---|---|---|
| `research/paper/manuscript.pdf` | 12 | manuscript title |
| `research/paper/supplementary.pdf` | 5 | STREAK supplementary material |
| `research/paper/supplementary_tables.pdf` | 24 (landscape) | STREAK supplementary tables (generated) |
| `research/experiments/EXP-001/report.pdf` | 8 | STREAK EXP-001 report |
| `research/experiments/EXP-002/report.pdf` | 8 | STREAK EXP-002 report |
| `research/experiments/EXP-003/report.pdf` | 8 | STREAK EXP-003 report |

Inspection findings, all fixed in the source or the builder: duplicated figure labels ("Figure 1: Figure 1."); a sentence in the EXP-001 report broken into a spurious numbered list (a wrapped line began with "0."; fixed with `--wrap=none`); a clipped x-axis label in the EXP-003 effects figure (generator `streak.frozen_analysis.effects_svg`, label now centred on the canvas; figure regenerated and copied, artifact manifest rebuilt); overlapping 64-character hashes in supplementary table S1 (hashes moved to lists under the table); a FIG-01b caption that mentioned a zero line outside the plotted range (caption corrected in the manuscript and the EXP-001 report); the LaTeX export double-numbered headings that already carry numbers (`manuscript.tex` regenerated without `--number-sections`). Metadata (pypdf): title set on all six; 0 e-mail addresses and 0 local paths in metadata or extracted text. Largest file 564,559 bytes.

## 5. Manifests, links and numbers

- `data/manifest.json`: raw Duolingo file SHA-256 `26cf9b33...` and `data/processed/first_repeat.npz` SHA-256 `6366c6de...` both match the local files.
- `research/publication/artifact_manifest.json`: 61 path references checked, all exist (one entry is the documented pattern `EXP-00N`); 17 of 17 recorded SHA-256 values match (result files and figures).
- Relative links: `scripts/check_links.py` checked 74 relative links in the tracked Markdown files: 0 broken (`LINK-CHECK PASS`); pytest `tests/test_links.py`.
- Numbers: the M5 consistency test covered decimal numbers in the README, CITATION, articles and demo README; M6 added counts with thousands separators and percentages (`test_public_texts_use_only_verified_counts_and_percentages`). `scripts/m4_evidence_audit.py`: every decimal number in the manuscript (171), reports and claims register traced, unmatched 0.

## 6. Secret, identifier and licence scan (tracked files, `git ls-files`: 298 before M6)

- E-mail addresses: 0. Tokens or keys (AWS, GitHub, OpenAI-style, Slack, `api_key=`, `secret=`, `password=`, `token=`): 0 real hits (1 false positive, the function name `matches(token, ...)` in `scripts/m4_evidence_audit.py`). Private key headers: 0. `.env` files: 0.
- Absolute home-directory paths: 15 lines in 10 files before M6 (plus 1 line in the new `scripts/build_pdfs.py`). Removed: 3 (`result_path` in the three `generated/frozen_analysis.json`, F-M6-2). Kept, with reason: `CLAUDE.md` (2, the documented shared tool locations), `research/feasibility.md` (4, toolchain table), `src/streak/report.py` (2) and `scripts/build_pdfs.py` (1, default tool paths, overridable with `STREAK_PANDOC` and `STREAK_TYPST_PYTHON`), the three `results/confirmatory/*/provenance.json` (frozen raw provenance, never edited) and `progress.md` (1, append-only; a note is appended).
- SPDX header: every text file added since M0 carries it, except three frozen `results/confirmatory/*/run.log` files (raw run logs, not edited); `demo/.npmrc` received it in M6.
- Dependency licences: `research/publication/dependency_licences.md`. No runtime dependency is non-permissive; one flag for information: pandoc (GPL-2.0-or-later) as an external build tool.

## 7. Final state of the working repository

```
$ .venv/bin/python -m pytest              231 passed
$ npm test (demo)                         43 passed
```

## 8. Fresh-clone recheck after the fixes (commit 10d5412)

```
$ git clone -q <repository> <scratch>/clone2; uv sync --frozen --all-groups --all-extras
$ .venv/bin/python -m pytest                                       231 passed in 9.37s
$ .venv/bin/python scripts/analyse_confirmatory.py EXP-001; ... EXP-003
$ .venv/bin/python scripts/export_demo_data.py --check             results.json up to date
$ .venv/bin/python scripts/check_links.py                          LINK-CHECK PASS
$ git status --short                                               0 lines (F-M6-2 fixed: regenerated analyses are byte-identical in a fresh checkout)
$ npm ci --prefer-offline; npm test; npm run build; node tools/a11y_check.mjs dist
  added 53 packages; Tests 43 passed (43); A11Y-CHECK PASS; git status 0 lines
```

Both scratch clones were deleted after the checks.
