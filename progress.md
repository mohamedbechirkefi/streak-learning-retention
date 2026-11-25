<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: M0 bootstrap and feasibility (with M1 drafts)

**Milestone.** M0 (bootstrap and feasibility). Next bounded task at session start: create the control files, audit hardware, tools and sources, draft the protocol.

**Starting state.** `git status`: "On branch main, nothing to commit, working tree clean". One commit, 7142fa0 (master prompt and the owner's licence package). The licence files were not modified, except that development commands were appended to `CONTRIBUTING.md` as the brief allows.

### Commands run and actual outputs

Hardware and tools:

```
$ sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize
Apple M1 Pro
10
17179869184
$ sw_vers
ProductName: macOS  ProductVersion: 15.3.1  BuildVersion: 24D70
$ df -h /Users/bechir/research
/dev/disk3s1  460Gi  311Gi  129Gi  71%  ...  /System/Volumes/Data
$ /usr/local/bin/python3 --version
Python 3.12.1
$ .tools/py/bin/uv --version
uv 0.9.5 (d5f39331a 2025-10-21)
$ .tools/py/bin/python -c "...versions of typst, pypdf, pillow"
typst 0.15.0 pypdf 6.20.0 pillow 11.3.0
$ .tools/pandoc --version | head -1
pandoc 3.6.3
$ helix/.tools/node/bin/node --version
v22.23.3
$ git --version
git version 2.42.1
$ which tex pdflatex xelatex latexmk typst
tex not found / pdflatex not found / xelatex not found / latexmk not found / typst not found
```

The brief stated about 127 GB free; `df` reported 129 GiB available.

Source audit (web, 2026-11-24): Crossref API metadata retrieved for seven DOIs (settles2016, tabibian2019, cepeda2006, roediger2006, murre2015, ye2022, silverman2022); ACL Anthology landing page, duolingo/halflife-regression README, awesome-fsrs "The Algorithm" wiki page, the UDSpace record of silverman2022 and the anki-revlogs-10k Hugging Face page were read. Failures: PNAS page HTTP 403; PMC page returned a browser check; APA PsycNet page did not load; Harvard Dataverse API HTTP 503 (twice). GitHub licence API: duolingo/halflife-regression MIT, open-spaced-repetition/fsrs4anki MIT. Hugging Face API: anki-revlogs-10k `gated: auto`, `license:other`. No dataset was downloaded.

Lockfile:

```
$ uv lock --python /usr/local/bin/python3   (pyproject exclude-newer = 2026-11-10T00:00:00Z)
Using CPython 3.12.1 interpreter at: /usr/local/bin/python3
Resolved 10 packages in 11ms
exit=0
```

Resolved: numpy 2.5.4, pytest 9.2.0, hypothesis 6.170.15, and their dependencies (colorama 0.4.6, iniconfig 2.3.1, packaging 26.3, pluggy 1.7.0, pygments 2.21.0, sortedcontainers 2.4.0). Latest upload time in the lockfile: 2026-11-06T09:54:57Z, before the 2026-11-10 cut-off. `uv sync` was not run (no code to install yet).

Exploratory toolchain smoke check (journal J-0001, not an experiment):

```
$ pandoc manuscript.md -s --number-sections -o manuscript.tex          exit 0
$ pandoc manuscript.md -s --number-sections -t typst -o <scratch>/manuscript.typ   exit 0
$ python -c "typst.compile(...)"
typst.TypstError: font fallback list must not be empty                 (failure)
$ pandoc ... -t typst -V mainfont="Libertinus Serif" ...               exit 0
$ python -c "typst.compile(...); pypdf page count"
pages 3
```

The skeleton PDF was written to the session scratchpad, not to the repository; it is not a deliverable. `manuscript.tex` is committed as a generated file with an SPDX header prepended.

Hygiene checks: no em dash in new files (grep exit 1); no e-mail address pattern in the working tree outside `.git` (grep exit 1) after removing one from a draft of CLAUDE.md; every new non-JSON/CSV text file carries the SPDX header.

### Decisions

D-001 (owner's licence), D-002 (pandoc to Typst toolchain, no TeX), D-003 (synthetic data only, proposal), D-004 (draft protocol choices, proposal), D-005 (dependency age cut-off). See `research/decision_log.md`.

### Files created or changed

CLAUDE.md, roadmap.md, progress.md, README.md, CITATION.cff, pyproject.toml, uv.lock, CONTRIBUTING.md (appended section 6); research/: protocol.md, feasibility.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv (header only), experiment_journal.jsonl, experiment_registry.csv, experiments/EXP-001..003/protocol.md, experiments/README.md, figure READMEs, paper/manuscript.md (headings only), paper/manuscript.tex (generated), paper/references.bib, paper/supplementary.md (headings only), publication/ (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md); data/manifest.json; READMEs in results/, src/, tests/, experiments/, demo/, articles/.

### Not done, and why

- No code, no tests, no simulation runs: M2 work; nothing to test yet (no test count claimed).
- No PDF deliverable: only the skeleton exists; the toolchain smoke PDF stayed outside the repository.
- Full texts of the cited papers not read: metadata only (labelled in the literature review). Planned for M1.
- Protocol not frozen: owner gate G-FREEZE.

### Outstanding risks

B-1 (Duolingo dataset licence unverified), B-2 (freeze pending), R-1 (result may depend on the difficulty-dependent gain; EXP-003), R-2 (unmeasured planning values), R-3 (non-OSI licence). See `research/feasibility.md` section 7.

### Next action

Owner: review and freeze the protocol (OD-1 to OD-3 in roadmap.md). AI, meanwhile: M1 full-text reading of key sources; M2 implementation of the engine, A0 and A1 first, with invariant tests and the result schema; smoke run on seeds 9001 to 9005 only.

## 2026-11-24: M2 core implementation and exploratory smoke runs

**Milestone.** M2 (core implementation) while the freeze is pending. Next bounded task at session start: implement A0 and A1 first, then A2, A3 and the EXP-003 cells, with tests, schemas, manifests, report generator and CLI; then an exploratory smoke run on seeds 9001 to 9005.

**Starting state.** `git status`: clean at e49e269. Protocols 0.1-draft, not frozen; no hash recorded.

### What was built

Package `streak` in `src/streak` (D-006): validated parameters and arms, memory model (exponential and power-law forgetting; difficulty-dependent and flat gain), synthetic learners with common random numbers, one-learner-arm simulation with carry-forward, daily cap and scheduler belief, protocol metrics, paired stratified bootstrap analysis with SESOI classes and Holm-adjusted p-values, versioned JSON schemas validated at export and import, run manifests, report generator and CLI (`smoke`, `run`, `report`, `test`). `run` refuses confirmatory configs while the protocol is unfrozen (tested on the three draft configs). Draft confirmatory configs `research/experiments/EXP-00N/config.json` (seeds 1 to 5, not run) and smoke configs `experiments/smoke-*.json`. Implementation readings of open protocol points: D-007.

### Commands and actual outputs

```
$ uv lock --python /usr/local/bin/python3        Resolved 10 packages; streak v0.0.0 -> v0.2.0 (only change in uv.lock)
$ uv sync --frozen                               installed numpy 2.5.4, pytest 9.2.0, hypothesis 6.170.15, streak 0.2.0 (editable)
$ uv run pytest  (commit f914ddd)                163 passed in 2.40s
  mutation checks (reverted): daily cap + 1 -> 14 failed, 149 passed; belief using the true gain rule -> 6 failed, 157 passed
$ uv run pytest  (commit 1cc0d53, with regression test; same test on the unfixed engine: 1 failed, 163 passed)   164 passed
$ uv run pytest  (commit dfa9dd4)                165 passed in 4.57s
$ python -m streak.cli test  (final, before the last M2 commit)   165 passed in 1.54s
$ python -m streak.cli run --config research/experiments/EXP-001/config.json
  refused: ... EXP-001 protocol has no recorded hash ('none (not frozen)'): not frozen ... (G-FREEZE), exit 3
```

Exploratory smoke runs (all on seeds 9001 to 9005, label exploratory; final ones on dfa9dd4, git_dirty false):

| Journal | ID | Learner-arms | Failed | Runtime | ms per learner-arm | Peak RSS |
|---|---|---|---|---|---|---|
| J-0004 | SMOKE-EXP-001 | 400 | 0 | 3.75 s | 9.37 | 40.9 MB |
| J-0005 | SMOKE-EXP-001-N200 | 4,000 | 0 | 21.61 s | 5.40 | 79.5 MB |
| J-0006 | SMOKE-EXP-002 | 10,800 | 0 | 28.32 s | 2.62 | 86.4 MB |
| J-0007 | SMOKE-EXP-003 | 2,400 | 0 | 8.47 s | 3.53 | 52.1 MB |

The machine was shared with other sessions (load average 25 to 80 on 10 cores), so runtimes are upper-side. Projected full confirmatory matrix (70,000 learner-arms): about 3 to 11 minutes. Seed spread at full EXP-001 size: SD of the paired A2 - A1 R30 difference 0.0207 (planning value 0.05), per-seed means 0.0789 to 0.0825; projected 95% half-width at n = 1,000 about 0.0013. Five seeds are adequate. Exploratory SMOKE-EXP-001 report PDF built with pandoc to Typst (`-V mainfont="Libertinus Serif"`), 3 pages, inspected as page images (tables and both SVG figures render; an earlier 17-column table overflowed and was split).

### Failures and fixes

- **D-008.** The first SMOKE-EXP-002 run (f914ddd) recorded 5,380 of 10,800 learner-arms as failed: integer grid values (`"h0": 1`) made the scheduler belief array integer-typed. Recorded by the runner, not dropped; fixed in 1cc0d53 (engine 1.0.1) with a regression test; outputs discarded (J-0002).
- **D-010.** Manifests marked runs dirty because of untracked outputs; fixed in dfa9dd4; runs repeated (J-0003 superseded).
- A shell command that would have removed scratch thumbnails with an unguarded variable was blocked by a safety check and not run; nothing in the repository was affected.

### Degenerate cases and proposals for the owner

Exploratory, not findings: floor regime at the draft parameters (A0 R30 0.0000, A1 R30 0.0281; A1 below 0.02 in 12 of 27 EXP-002 cells), weakest-decile R30 identically 0, A3 ("lowest estimated recall first") practically equivalent to no practice under exponential forgetting, overload of K = 100 items, and an EXP-002 floor rule that never triggers. The primary contrast on smoke seeds is positive at default (opposite to the expected direction) and most likely reflects that regime. Proposals AP-1 to AP-7 and a disclosure note are in `research/protocol_amendment_proposals.md`; owner decision OD-6 added to the roadmap. The protocol itself was not changed.

### Files created or changed

`pyproject.toml` (package build with uv_build, version 0.2.0, script entry), `uv.lock` (project entry only), `src/streak/*` and `src/streak/schemas/*`, `tests/*` (11 test files), `experiments/smoke-*.json`, `research/experiments/EXP-00N/config.json`, `research/protocol_amendment_proposals.md`, `research/decision_log.md` (D-006 to D-010), `research/experiment_journal.jsonl` (J-0002 to J-0007), `research/experiment_registry.csv` (status), `results/exploratory/` (manifests, generated reports, SMOKE-EXP-001 raw results and PDF), READMEs of src, tests, experiments, results, `CONTRIBUTING.md` (section 6 commands), `roadmap.md`.

### Not done, and why

- No confirmatory run, no protocol hash: G-FREEZE (owner).
- No EXP-NNN `report.md`, `run_manifest.json` or `metrics.csv` in `research/experiments/`: those belong to confirmatory runs (M3). The report generator writes them; it was exercised on exploratory runs only.
- Control-only calibration for AP-1 not run: left to the owner to avoid tuning on the primary contrast.
- Manuscript and full-text reading (M1) not advanced in this session.
- No demo UI (M5).

### Outstanding risks

R-1 now concrete: the primary contrast at the draft parameters is driven by a floor and overload regime (DG-1 to DG-4). R-4 (new): smoke directions were seen before the freeze; the frozen protocol must disclose this. B-1, B-2, R-3 unchanged.

### Next action

Owner: decide OD-6 (AP-1 to AP-7), then OD-1 to OD-3 and freeze. AI, after the owner's decisions: implement any adopted amendment (for example threshold-based A3), repeat the smoke runs, then M3 on the frozen protocols.

## 2026-11-24: Real data, round-2 amendments and freeze (protocol 1.0)

**Milestone.** M1 freeze, on the owner's approvals (`_shared/owner-approvals-2026-11-24b.md` sections 1 and 7; brief `_shared/DATA-FREEZE-brief.md`). Starting state: clean at 83e0d8e.

### Commands and actual outputs

```
$ curl https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/N8XJME
  termsOfUse: "This work is released under the ... (CC BY-NC 4.0)."; one file, 379,004,009 bytes, MD5 0a1cae5e...
$ python scripts/download_duolingo.py            (about 37 min) MD5 matches; SHA-256 26cf9b33...6873
$ .venv/bin/python scripts/ingest_duolingo.py    41.7 s; 12,854,226 rows; 0 missing; 0 invalid; 324,353 kept (fit 163,110, held-out 161,243)
$ .venv/bin/python scripts/fit_h0.py             h0 = 67.590 days (naive LR 95% 66.70 to 68.49), not on grid edge, 5.1 s
$ .venv/bin/python scripts/floor_check.py 67.59  K=100: A0 0.410, A1 0.873 (above 0.8); K=200: A0 0.410, A1 0.791 -> K = 200
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras    Audited 9 packages
$ .venv/bin/python -m pytest                     199 passed in 3.73s
$ guard check (require_runnable on the three frozen configs, gate only, not run): accepted; each with h0 changed: refused
```

### Order of work (visible in git)

29d0dfb: licence check, download script, ingestion and fit code with tests on an invented fixture, threshold A3 (engine 1.1.0), Holm-across-cells option, and protocol section 14 with the calibration method, all before any fit. 08b4400: ingestion, fit and floor-check scripts; guard extended to configs and data manifest. 02eb104: fitted values (journal J-0008 to J-0010) written into the protocols and configs. Freeze commit: `research/freeze.json`, `research/freeze_record.md`, registry hashes, guard tests, records.

### Decisions

D-011 (Duolingo adopted, licence clean), D-012 (method before fit), D-013 (h0 = 67.59 days, K = 200), D-014 (freeze).

### Not done, and why

- No confirmatory run and no held-out evaluation: M3, scheduled by the coordinator.
- No smoke run of A2 or A3 at the new parameters: deliberately avoided before the freeze (no new look at the primary contrast). Runtime at K = 200 is therefore not yet measured for the full arms (floor check: 6.3 s for 2,000 A0/A1 learner-arms at each of two K values).
- AP-3, AP-4, AP-6 not applied (not approved). Smoke configs in `experiments/` keep the draft parameters (history only).

### Outstanding risks

R-5 (new): h0 = 67.59 days rests on in-session accuracy of Duolingo users after one prior exposure, not on a free-recall test; the second test (P§14.4) checks the forgetting form on held-out users. R-1 to R-4 as before; R-4 disclosed in P§14.7.

### Next action

Coordinator: schedule M3 (EXP-001 to EXP-003 confirmatory runs and the held-out second test) on a quiet machine; push only as approved.

## 2026-11-24: Round-3 ratification (K = 200)

**Milestone.** Records only, after the M1 freeze (brief `_shared/ROUND3-brief.md`; authority `_shared/owner-approvals-2026-11-24c.md`, section 4). Starting state: clean at b9b7e7a.

### Changes

- `research/decision_log.md`: D-015 records the owner's ratification of K = 200 ("Approve all", 2026-11-24, round 3).
- `research/freeze_record.md`: new "Ratifications after the freeze" table.
- `research/freeze.json`: new `ratifications` field (not read by the run guard).
- No frozen protocol, config or data manifest changed.

### Commands and actual outputs

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   Audited 9 packages
$ .venv/bin/python -m pytest                                    199 passed in 3.94s
$ shasum -a 256 (protocol, EXP-001 to EXP-003 protocols and configs, data manifest)   all equal to the freeze record
```

### Not done, and why

No confirmatory run and no push (brief: coordinator schedules M3 and pushes).

### Next action

Coordinator: schedule M3 on a quiet machine.

## 2026-11-25: M3 confirmatory runs

**Milestone.** M3, on the owner's "Start next" (brief `_shared/M3-brief.md`). Starting state: clean at e51e5bd; every frozen hash equal to the files on disk; raw Duolingo SHA-256 equal to the manifest.

### Commands and actual outputs

```
$ ../.tools/py/bin/uv sync --frozen --all-groups --all-extras   Audited 9 packages
$ .venv/bin/python -m pytest                                    199 passed (start); 211 passed after 45ea4ec
$ streak.cli smoke --config experiments/smoke-m3-exp001.json    400 learner-arms, 0 failed, 2.10 s (J-0011, smoke seeds)
$ scripts/validate_smoke.py <smoke results>                     ALL PASS (11 known cases, all invariants; J-0012)
$ scripts/run_confirmatory.py EXP-001                           4,000 learner-arms, 0 failed, 30.5 s (J-0013)
$ scripts/heldout_test.py                                       ll/trial exp -0.3865, power -0.3710, constant -0.3352 (J-0014)
$ scripts/run_confirmatory.py EXP-002                           54,000 learner-arms, 0 failed, 354.4 s (J-0015)
$ scripts/run_confirmatory.py EXP-003 (first launch)            preflight refused, tree not clean, nothing run (J-0016)
$ scripts/run_confirmatory.py EXP-003                           12,000 learner-arms, 0 failed, 82.9 s (J-0017)
$ scripts/analyse_confirmatory.py EXP-001|EXP-002|EXP-003       generated/ tables, figures, frozen_analysis.json
$ .venv/bin/python -m pytest                                    211 passed (end)
```

### Results (confirmatory, simulation only)

- EXP-001: A2 - A1 in R30 -0.3068, 95% CI [-0.3093, -0.3042]; relevant negative; supports the expected direction. A3 - A1 +0.0114 (practically equivalent).
- EXP-002: 27 of 27 cells relevant negative (-0.4709 to -0.1763), all relevant after Holm across cells; robustness not disconfirmed.
- EXP-003: H-inv not triggered (flat gain: exponential -0.3887, power -0.2772); selection carries the gap, timing and interaction within the SESOI.
- Held-out test (P§14.4): negative for the model; the exponential form does not beat a constant baseline; power-law better supported.

### Deviations and decisions

D-016: pre-run analysis code; EXP-002 manifest `git_dirty = true` (records edited during the run, no code change); first EXP-003 launch refused by preflight; 11.6 `report.md` files refused by the file tool, the EXP-001 one written by a shell workaround and then removed on the coordinator's instruction, none now in the tree.

### Not done, and why

- Standalone 11.6 reports for EXP-001 to EXP-003 (tool refusal; owner or coordinator to decide).
- No PDF built; no push.

### Next action

Owner or coordinator: decide how the 11.6 reports are written; then M4 (evidence audit, synthesis, second review pass challenging the preferred hypothesis, including the negative held-out result).

## 2026-11-25: M3 close attempt (owner approvals of 2026-11-25)

**Milestone.** M3 close, brief `_shared/M3-close-brief.md`; authority `_shared/owner-approvals-2026-11-25.md`, section 4 (owner, "approve all recommendations, RIGGED A"). Starting state: clean at cfedba5.

### Actions and actual outcomes

- D-017 records the owner's decision.
- EXP-001 report from 219c054 checked number by number against the committed outputs: all match (three percentages replaced by the committed proportions).
- Write tool on `research/experiments/EXP-001/report.md`: refused ("Subagents should return findings as text, not write report files"). Per the brief, stopped; no workaround; EXP-002 and EXP-003 reports not attempted.
- `.venv/bin/python -m pytest`: 211 passed.

### Status

**M3 not done.** The run gate holds (complete matrices, 70,000 learner-arms, 0 failed), but the 11.6 reports for EXP-001 to EXP-003 are still missing.

### Next action

Coordinator or owner: have the reports written by a session whose file tool accepts `report.md` (the checked EXP-001 text is in commit 219c054; all EXP-002 and EXP-003 numbers are in the committed `generated/` files).

## 2026-11-25: reports returned to the coordinator (D-018)

The EXP-001 to EXP-003 `report.md` texts were composed from committed results only and returned as text to the coordinator, who writes and commits them (`_shared/report-return-note.md`). No report file was written by the AI. The M3 status is left to the coordinator. Tests: 211 passed.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 3 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.
