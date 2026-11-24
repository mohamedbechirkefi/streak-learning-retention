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
