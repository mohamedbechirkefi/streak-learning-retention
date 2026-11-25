<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Claims and evidence audit (M4, 2026-11-25)

Master prompt 11.5. Object: `research/paper/manuscript.md` 1.0, `research/paper/supplementary.md`, `supplementary_tables.md`, the reports of EXP-001 to EXP-003, `research/publication/review_pass_2.md` and `research/claims_register.csv`. Performed by the AI research assistant as internal quality control. The owner reviews it. Journal J-0019, decision D-019.

## 1. Method

| Check | How | Tool |
|---|---|---|
| Raw-file integrity | SHA-256 of each confirmatory `results.json` against `sha256_manifest.json` | `scripts/m4_evidence_audit.py` |
| Denominators and sample counts | records, failures and learners per cell recomputed from raw records; compared with `generated/contrasts.csv` | same |
| Primary estimates | mean A2 - A1 per cell recomputed from raw records; tolerance 1e-12 | same |
| Every printed number | each decimal with two or more decimals (DOIs excluded) must equal, at its printed precision and with its sign, a value in a committed output (generated tables, frozen analyses, held-out test, calibration, floor check, run manifests, M4 exploratory summary, protocols, journal) | same; result in `evidence_audit.json` |
| Semantic table checks | EXP-001 table 8.1 (all arms and metrics), EXP-002 table 8.1 (27 rows: mean, CI, rounded A1 and A2 means, class), EXP-003 table 8.1 (24 values) against the generated CSVs; residual-flag counts recomputed from raw records | ad hoc checks, M4 session (commands in `progress.md`) |
| Units and precision | R30 and recall as proportions in [0, 1]; minutes = slots × 0.5; days; four decimals for contrasts, two or three for descriptive means | reading |
| Uncertainty | 95% and 90% stratified bootstrap intervals; Holm only where frozen; "< 0.0001" for bootstrap p = 0 | reading against `generated/` |
| External claims | each cited statement against a source actually read, with verification level | `research/literature_review.md`, section 4 |
| Mapping | every claim to a result id, config hash, figure or table and section | `research/claims_register.csv`, `artifact_manifest.json` (`scripts/m4_build_artifact_manifest.py`) |

## 2. Results

- **Integrity.** All three raw files match their manifests (EXP-002's 31.8 MB file is git-ignored and was present locally).
- **Counts.** 4,000, 54,000 and 12,000 records; 0 failed; 1,000, 500 and 500 learners per cell. All equal the reports.
- **Primary estimates.** All 32 primary means (1 + 27 + 4) recomputed; largest absolute difference from the committed tables 5.6e-17.
- **Residual flags.** EXP-001: 6 flagged learner-arms (3 learners, A2 and A3). EXP-002: 360 (at most 18 in one cell-arm). EXP-003: 12 (one learner per variant). All equal the reports.
- **Number trace.** 3,234 printed decimal numbers checked across 8 documents. After the fixes below, 0 are unmatched (`evidence_audit.json`). Limit of this check: a two-decimal number can match an unrelated value by chance. Two-decimal numbers in the tables were therefore also covered by the semantic checks.
- **Semantic checks.** EXP-001, EXP-002 and EXP-003 tables 8.1: no mismatch.
- **Figures.** The four manuscript figures are byte-identical copies of the generated figures (`artifact_manifest.json`, `copy_sha256_matches`).
- **Mapping.** 25 claims, each with a result id (or "n/a" for external claims), config or protocol hash, figure or table and section. No claim lacks a result entry in the manifest.

## 3. Findings and fixes

| # | Finding | Severity | Fix |
|---|---|---|---|
| F-1 | EXP-003 report section 9 says timing contrasts change R30 "by at most 0.0188". 0.0188 is a selection contrast (A3 - D-RR, exp-flat). The true maximum timing contrast is 0.0150 (A2 - F-EASY, exp-diff). | error in a report (conclusion unchanged) | correction in the EXP-003 report's M4 audit note; the original sentence is left visible |
| F-2 | Reports cite Cepeda et al. (2006) for "spacing improves long-term retention" and "supports spacing benefits". Only metadata had been verified, and the abstract now read does not state the direction. | external claim overstated | qualified in the M4 notes of EXP-001 and EXP-003; the manuscript cites only what the abstract states |
| F-3 | Other external citations (Roediger and Karpicke, Murre and Dros, Tabibian et al.) rested on metadata only | verification gap | abstracts read on 2026-11-25 (Europe PMC records and the PLOS page); Settles and Meeder read in full for the cited points; levels recorded in `literature_review.md` section 4 and in the claims register (CLM-E01 to CLM-E08) |
| F-4 | `experiment_registry.csv` still said "report.md not written" | stale record | status updated |
| F-5 | FSRS documentation and the Duolingo dataset were cited but missing from `references.bib` | missing references | entries `fsrswiki` and `duolingodata` added; the dataset's own title and creators were not recorded at access time and are not invented |
| F-6 | Figure IDs repeat across experiments (FIG-01a in EXP-001, EXP-002 and EXP-003 with different content) | labelling ambiguity | the manuscript uses experiment-qualified copies (`EXP-00N_FIG-...`); report-internal IDs unchanged |
| F-7 | `generated/frozen_analysis.json` records an absolute local path as `result_path` | provenance detail (machine path in a committed file) | recorded; not regenerated, because no number depends on it |
| F-8 | Manuscript draft 0.9 printed magnitudes of negative contrasts without sign (0.3068 with CI 0.3042 to 0.3093; 0.2358) | precision and sign convention | rewritten as signed values |
| F-9 | Claims register lacked config hash, figure and section columns, and had no external-claim rows | incomplete register | columns added; 10 claims and 8 external-claim rows added; CLM-003 qualified |
| F-10 | `artifact_manifest.json` was empty (M0 placeholder) | missing manifest | generated by `scripts/m4_build_artifact_manifest.py` |

No number, verdict or frozen file changed.

## 4. Strength and scope of evidence per conclusion

| Conclusion | Strength | Scope |
|---|---|---|
| A2 retains less than A1 at matched minutes | strong within the model (confirmatory, every learner, every cell, every variant) | frozen model; stylised A2; synthetic learners |
| Selection, not timing, carries the gap | strong within the model (confirmatory 2 × 3 design, 4 variants) | same; timing small but non-zero with easiest-first |
| Gap size | weak as an external quantity | depends on K and h0 (exploratory); time scale not validated |
| A3 matches A1 | moderate, conditional | default and longer half-lives; fails at h0 = 33.8 days and K = 400 |
| Exponential forgetting not supported on real first repeats | moderate (preregistered, descriptive, one dataset) | Duolingo in-session accuracy; σ fixed; naive likelihood |
| Floor-regime sign reversal | exploratory, seen before the freeze | draft parameters |

## 5. Checklist

- [x] Each numerical claim maps to a result id, run ids, config and figure or table in `artifact_manifest.json`.
- [x] Each external claim maps to a source actually opened, with the verification level stated.
- [x] Type, scope and limitations recorded in the claims register.
- [x] No claim about real human learning efficacy, proprietary systems or causal human behaviour.
- [x] Numbers re-audited against raw outputs: denominators, units, precision, uncertainty, sample counts.
- [x] Second review pass that challenges the preferred hypothesis completed and recorded (`review_pass_2.md`).
- [x] Unsupported claims removed or qualified.
- [ ] Owner review of this audit (owner).

## 6. M6 reference check (2026-11-25)

Every entry of `research/paper/references.bib` (9 entries) is cited in the manuscript reference list (DOI or URL match, 9 of 9), and every manuscript reference has a bib entry. The manuscript uses author-year text citations, not pandoc citation keys, so key resolution was checked by DOI and URL. For each source not yet read in full, a free and legal full text was sought (no paid access, no login, no shadow library). Access date for all: 2026-11-25.

| Key | Reading level after M6 | Copy read | Cited point checked (location) |
|---|---|---|---|
| settles2016 | read in full (relevant sections, M4) | ACL Anthology PDF | equation (1), section 4.1, Table 2 (M4) |
| cepeda2006 | **read in full (M6)** | author-hosted PDF, https://www.yorku.ca/ncepeda/publications/CPVWR2006.pdf | p. 354 abstract: "the ISI producing maximal retention increased as retention interval increased"; p. 358: "Spaced presentations led to markedly better final-test performance, compared with massed presentations". The M4 qualification of "spacing improves long-term retention" (EXP-001 and EXP-003 reports) is resolved: the source supports it for the verbal recall tasks it reviews. |
| roediger2006 | **read in full (M6)** | author-hosted PDF, http://learninglab.psych.purdue.edu/downloads/2006/2006_Roediger_Karpicke_PsychSci.pdf | p. 249 abstract and the Experiment 1 and 2 designs: prose passages; at 5 min restudy beat testing, on the delayed tests (2 days, 1 week) prior testing gave greater retention. Matches the manuscript sentence. |
| murre2015 | **read in full (M6)** | open-access article page, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0120644 | Abstract and Discussion: "a successful replication of Ebbinghaus' classic forgetting curve from 1880 based on the method of savings". In the Discussion the summed-exponential (MCM) function fits best on average, by margins the authors treat as modest; the manuscript makes no functional-form claim from this source, so nothing changes. |
| silverman2022 | **read in full (M6, accepted manuscript)** | University of Delaware repository, pre-copyedited accepted manuscript, https://udspace.udel.edu/bitstreams/7e3e3b64-8bf2-4527-ac93-94a160358165/download | Abstract (manuscript p. 3) and General Discussion: "In seven studies, we find that intact streaks highlighted via behavioral logs increase consumers' subsequent engagement in that behavior, relative to when broken streaks are highlighted." Matches. Year: published online 2022, issue 49(6) dated 2023; the bib entry carries 2023 and the text 2022, both stated in `research/literature_review.md`. |
| tabibian2019 | abstract only | arXiv preprint abstract, https://arxiv.org/abs/1712.01856 (titled "Optimizing Human Learning", same authors; v2 2018-03-10) | "the optimal reviewing schedule is given by the recall probability of the content to be learned". The published PNAS version was not opened (HTTP 403 in M0); the claim stays worded as what the abstract reports. |
| ye2022 | unverified (metadata only) | ACM Digital Library PDF returned HTTP 403 | Cited only as an example of scheduler-optimisation work, with no statement about its content (manuscript section 2.2 already says so). No change. |
| fsrswiki | read in full (web page, M0) | GitHub wiki page | power-law forgetting curves in FSRS (M0) |
| duolingodata | read (dataset record and licence, M0) | Harvard Dataverse record | CC BY-NC 4.0; file hash in `data/manifest.json` |

Counts: read in full 7 (5 articles plus 1 web page and 1 dataset record), abstract only 1, unverified 1. Claims qualified: none newly; the M4 qualification on Cepeda et al. is resolved by the full text and recorded in M6 audit notes appended to the EXP-001 and EXP-003 reports. The manuscript reference list now states, for the four sources upgraded, where the cited point was checked.
