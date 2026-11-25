<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Release checklist

Status at M0: not started. Publication is owner-controlled (G-PUBLIC); nothing is pushed or published without explicit approval.

**Status (M6, 2026-11-25): release candidate prepared (`CITATION.cff` version 0.1.0-rc1), awaiting the owner's review and G-PUBLIC. Nothing is pushed, tagged or published.** Items ticked below were verified in the M6 session, with the evidence named; the two owner items stay open.

- [x] Every registered experiment has a truthful standalone report (including failed, null or exploratory ones). Evidence: `research/experiment_registry.csv` lists EXP-001 to EXP-003; each has `report.md` and a compiled, inspected `report.pdf` (8 pages each); the held-out test, the floor regime and the M4 sensitivity checks are reported in the manuscript (sections 5.4 to 5.6) and the reports.
- [x] Integrated manuscript complete; abstract written after analysis. Evidence: `research/paper/manuscript.md` 1.0 (5,311 words by `wc -w`, including front matter and references), `manuscript.pdf` 12 pages inspected page by page; `manuscript.tex` regenerated.
- [x] All artifacts traceable through `artifact_manifest.json`. Evidence: rebuilt with `scripts/m4_build_artifact_manifest.py` ("results 17, figures 4, tables 4, claims 25, missing []"; "figure copies match: True"); 61 path references exist; 17 of 17 SHA-256 values match.
- [x] Demo, paper, reports and articles use identical verified results, labels and scope. Evidence: `tests/test_demo_consistency.py` (10 tests, including the M6 extension to counts and percentages) and `scripts/m4_evidence_audit.py` (unmatched 0) pass; full suite 231 passed.
- [x] README shows status, experiment table, key results and limitations, one-command reproduction. Evidence: `README.md` sections Status, Key results, Research navigation (experiment table), Limitations, Quick start; all 74 relative links in tracked Markdown resolve (`scripts/check_links.py`, LINK-CHECK PASS).
- [x] `reproducibility_report.md` completed with actual outputs. Evidence: clean clone of `ff06d8d`, 225 passed, smoke run byte-identical, A11Y-CHECK PASS, export determinism (0 changed files); findings F-M6-1 and F-M6-2 recorded.
- [x] `claims_audit.md` and `author_review.md` completed. Evidence: `claims_audit.md` section 6 (M6 reference check: 7 read in full, 1 abstract only, 1 unverified); `author_review.md` section "Prepared for the owner (M6, 2026-11-25)". The boxes in `author_review.md` are the owner's and are not ticked.
- [x] Remaining blockers explicitly disclosed. Evidence: `author_review.md` lists every open owner decision and placeholder with file and line; `progress.md` M6 entry.
- [ ] Owner sign-off of `author_review.md` (owner).
- [ ] Owner approval to publish recorded in `research/decision_log.md` (owner; OD-5, G-PUBLIC).
