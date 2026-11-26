<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# STREAK: how every session works in this repository

Project: *When can activity streaks diverge from knowledge retention in a learning model?*
All results are simulations of synthetic learners. The owner holds final authority over hypotheses, protocol freezes, design decisions, claims, authorship and publication. The AI is a disclosed research and development assistant, never the investigator.

## 1. Reading order (mandatory, before modifying anything)

1. `master_prompt.md` (the authority; never edit it)
2. `roadmap.md`
3. `progress.md`
4. `research/protocol.md`
5. `research/claims_register.csv`

Then also check `research/decision_log.md`, `research/experiment_registry.csv` and `git status`. If resuming, do not overwrite owner changes. State the current milestone and the next bounded task before starting work.

## 2. Session protocol

- Work in small reviewable changes. Run the relevant tests after each change and record the actual output, never the expected one.
- Update `roadmap.md` and `progress.md` after every milestone and before ending a session. `progress.md` is append-only: dated entry with decisions, commands, actual results, failures, changed files, outstanding risks and next action.
- Record every non-trivial decision in `research/decision_log.md` (append-only, numbered D-NNN).
- Record every run (exploratory or confirmatory) in `research/experiment_journal.jsonl`.
- Never mark incomplete work done. Never silently change research scope, metrics, architecture or dependencies.
- If blocked, document it and choose the smallest lawful offline fallback, clearly distinguished from the original research.
- If the five-day target is threatened, cut optional UI and optional experiments first, never controls, reporting or truthfulness.

## 3. Mandatory requirements of master prompt section 11 (apply in every session)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex generated, references.bib, figures/, supplementary.md, manuscript.pdf generated locally after validation), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN ids for runs, FIG ids for figures, CLM ids for claims. A seed is a run inside an experiment, not a new experiment. A new question or materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** A complete `EXP-NNN/protocol.md`, frozen with version and hash and owner approval before held-out results are evaluated. Post-hoc changes are exploratory, dated and justified.
- **Per-experiment report (11.3).** Every registered experiment, including failed, null, abandoned and exploratory ones, gets a standalone report with the 12 mandatory sections. Reports link to their own machine-readable outputs. Tables and figures are generated from actual outputs, never copied by hand or mocked.
- **Manuscript (11.4).** One integrated manuscript, 3,000 to 6,000 words where the evidence justifies it, with the required structure. Default status: independent research manuscript, preprint draft, not peer reviewed. No invented affiliations, funding, endorsements or citations.
- **Evidence pipeline (11.5).** One local report-generation command. Figures and tables are generated once from versioned results and reused everywhere. A manifest maps every quantitative figure, table and claim to experiment id, run ids, metric definition, result path, generator script, config or protocol hash and code revision. A second review pass must challenge the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1 registry, skeleton, experiment protocols, zero-cost toolchain, freeze before execution. M2 versioned schemas, manifests and report generators alongside the core. M3 reports as experiments finish, provenance captured immediately. M4 evidence audit and synthesis including contradictions. M5 identical verified results across demo, paper, reports and articles. M6 compile and inspect PDFs, verify references, clean-clone smoke reproduction, owner review checklist.
- **Toolchain (decision D-002).** No TeX distribution is installed. PDFs are built as pandoc Markdown to Typst, compiled with the `typst` Python package; `manuscript.tex` is generated from Markdown with pandoc and is not compiled locally. Never claim that a PDF exists unless it was generated and inspected.

## 4. Rules (all sessions)

### Gates
- **G-PUBLIC.** Never push, add a remote, create a GitHub repository or publish anything.
- **No paid service** of any kind (APIs, inference, data, compute, hosting, domains). The coding subscription is never an inference backend.
- **G-FREEZE.** Never freeze a protocol yourself: freezing is the owner's decision. Until the owner freezes `research/protocol.md` and the EXP protocols, run no confirmatory experiments. Tiny exploratory smoke checks are allowed and must be labelled exploratory, and they use only the smoke seed range (never the confirmatory seeds).

### Scope
- Work only inside this repository. Read-only use of the shared tools: `/usr/local/bin/python3`, `../.tools/py/bin/` (uv, typst, pypdf, pillow), `../.tools/pandoc`, Node at `../../helix/.tools/node/bin` (read-only, never modify that folder), and git; the `..` paths are relative to this repository.
- Do not touch any other folder under the research root, the folder two levels above this repository (hive, helix, cogkt, trading, other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs.
- Anything not verified is labelled unverified. Only cite sources actually opened, with URL or DOI and access date.
- Simulated learners are not humans: no claims about real human learning efficacy without human evidence, no claims about any proprietary product's internals, no pressure-based or manipulative UX.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0` as a comment where the format allows; JSON and CSV are covered by `NOTICE.md`.
- Do not change the licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`). Development commands may be appended to `CONTRIBUTING.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them if needed).
- Large generated outputs stay out of git (`results/raw/`); provide deterministic regeneration scripts and small fixtures.

### Commits
- Local commits only: `git -c user.name=mohamedbechirkefi -c user.email=<owner's git e-mail> commit`, using the e-mail given in the owner's session brief (deliberately not stored in this file, which must contain no e-mail address). The message ends with a blank line, then the Co-Authored-By trailer for Claude Opus 5.5 exactly as given in the owner's session brief. Run `git status` before and after.
