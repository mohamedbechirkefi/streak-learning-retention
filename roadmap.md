<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# STREAK roadmap

Target: five focused development days (planning estimate, never a reason to weaken evidence). Status values: done, in progress, not started, blocked. Section 11.6 additions of the master prompt are mandatory and listed under each milestone.

Current milestone: **M0 done (pending owner review); M1 in progress (drafts written, freeze pending).**

## Owner decisions needed

| ID | Decision | Blocks |
|---|---|---|
| OD-1 | Approve or change the question restatement, H0/H1, primary metric R30, baseline A1 Fixed and SESOI 0.02, then freeze `research/protocol.md` and the three EXP protocols (G-FREEZE). | M3 confirmatory runs |
| OD-2 | Confirm the experiment set (EXP-001 to EXP-003) and that EXP-003 (the invalidating sensitivity) stays in scope. | M1 freeze |
| OD-3 | Confirm synthetic-only data (D-003); no calibration to real traces (Duolingo dataset licence unverified, B-1). | M1 |
| OD-4 | Approve authorship metadata and AI-assistance disclosure wording. | M4, M6 |
| OD-5 | Any publication or push (G-PUBLIC). | M6 release |

## Milestones

| ID | Milestone | Depends on | Acceptance criteria | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | Control files of master prompt section 2 and 11.1 tree exist; feasibility audit with confirmed hardware and tools; source and licence audit; scope, exclusions and fallback stated; zero-cost toolchain confirmed (11.6); registry initialised; manuscript skeleton; lockfile; local commit. Gate: the owner can understand the question, cost and exclusions. | P0 | 0.5 day | done (awaiting owner review) | none |
| M1 | Research and preregistration | M0 | Evidence review with verified sources (full texts of key sources read or labelled metadata-only); formal model; baselines; protocol and EXP-001 to EXP-003 protocols complete per 11.2; fixture manifest; smoke run on smoke seeds only to check floor effects and variance; **owner freezes protocols, hashes recorded in the registry (11.6)**. Gate: protocol frozen before confirmatory runs; exploratory results visibly separated. | P0 | 0.25 day plus owner review | in progress (drafts done; full-text reading and freeze pending) | OD-1, OD-2, OD-3 |
| M2 | Core implementation | M1 drafts (not the freeze) | Reference baseline A1 and A0 first, then A2, A3 and EXP-003 cells; memory model in both forms and both gain rules; unit, invariant, golden and differential tests per protocol section 8, actually run; **versioned JSON result schema, run manifests (runtime, peak memory, OS, CPU, package versions, git revision, config) and report generator built alongside the core (11.6)**; CLI smoke, run, report, test. Gate: correctness before UI. | P0 | 1.5 days | not started | none (can start before the freeze; only confirmatory runs wait) |
| M3 | Experiments | M2, owner freeze (OD-1) | Smoke run validated; frozen matrices of EXP-001 to EXP-003 run in full with confirmatory seeds; raw machine-readable results retained; plots and uncertainty generated from outputs; **individual reports generated as each experiment finishes; failures and deviations recorded; provenance captured immediately (11.6)**. Gate: complete planned matrix or documented failure; no silently dropped runs. | P0 | 0.75 day | not started | OD-1 |
| M4 | Interpretation | M3 | Confounders inspected; sensitivity analyses (EXP-003 invalidation test, residual exclusion); expected versus observed; claims register populated; limitations; **experiment reports finished, evidence audit, cross-experiment synthesis in the manuscript including contradictory results (11.6)**; second review pass challenging the preferred hypothesis. Gate: every numerical claim maps to result ID, config and figure; every external claim to a verified source. | P0 | 0.75 day | not started | M3 |
| M5 | Interactive experience | M4 (results), M2 (engine) | Static page: learning timeline, memory curves, streak versus recall comparison; playground with reset, seed and scenario controls; published results separated from sandbox results; accessibility (keyboard, contrast, reduced motion, mobile); offline after load; no runtime service; **demo, paper, reports and articles use identical verified results, labels and scope (11.6)**. | P1 (optional parts cut first) | 0.75 day | not started | M4 |
| M6 | Release candidate | M4, M5 | Clean clone into a separate directory; `uv sync --frozen`; tests and smoke reproduction; demo build; manifests and links verified; secret and licence scan; **manuscript and report PDFs compiled via pandoc to Typst and visually inspected; references, cross-links, equations, figures and metadata verified; owner review checklist completed (11.6)**. Gate: verified facts only; owner approves any publication. | P0 | 0.5 day | not started | OD-4, OD-5 |

## Dependencies

M0 → M1 drafts → M2 (implementation can proceed while the freeze is pending) → owner freeze → M3 → M4 → M5 → M6. EXP-002 and EXP-003 depend on the EXP-001 engine and tests, not on EXP-001 results.

## Cut order if the five-day target is threatened

1. Demo polish and optional demo views. 2. EXP-003 power-law variant. 3. EXP-002 grid size (keep at least the h0 axis). Never cut: controls, invariant tests, reports for every registered experiment, provenance, truthfulness.
