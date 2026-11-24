<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Pre-freeze amendment proposals for the owner (from the M2 exploratory smoke runs)

| Field | Value |
|---|---|
| Date | 2026-11-24 |
| Status | **Proposals only.** Nothing here changes `research/protocol.md` or the EXP protocols, which remain 0.1-draft and not frozen. The owner decides (G-FREEZE). |
| Evidence | Exploratory smoke runs on development seeds 9001 to 9005 only, engine 1.0.1, commit dfa9dd4: journal J-0004 to J-0007; outputs in `results/exploratory/`. |
| Label | Every number below is **exploratory**. None is a finding or may be cited as a result of EXP-001 to EXP-003. |

## Disclosure that matters for the freeze

The smoke runs computed the primary contrast on smoke seeds, so the direction of A2 minus A1 at the draft parameters is now visible to whoever reads `results/exploratory/`. At the default parameters it is positive (A2 above A1, the opposite of the preregistered expected direction; the test is two-sided), and it is positive in 22 of the 27 EXP-002 smoke cells. Section 1 below explains why this is very likely a property of a degenerate regime rather than of streak-driven timing. Because the owner may now amend the protocol after seeing smoke directions, the AI recommends that (a) any amendment be justified only by the degeneracy criteria below, which concern the controls and the operationalisation, not the primary contrast, and (b) the frozen protocol state that the smoke results on seeds 9001 to 9005 were seen before the freeze.

## 1. Degenerate cases found

| ID | Observation (exploratory) | Source |
|---|---|---|
| DG-1 Floor | At default parameters A0 has R30 = 0.0000 (closed form 2^(-86/h) with median h about 1 day) and A1 has R30 = 0.0281 (n = 1,000 smoke learners). In the EXP-002 smoke grid, A1 has mean R30 below 0.02 in 12 of 27 cells. | J-0005, J-0006 |
| DG-2 Weakest decile | Weakest-decile R30 is 0.0000 for every arm in every EXP-001 and EXP-002 smoke cell (largest A1 value in the grid about 5e-41). As defined, the metric carries no information in this regime. | J-0005, J-0006 |
| DG-3 A3 operationalisation | A3 ("lowest estimated recall first") reviews items that are already lost: practice success rate 0.020 and R30 0.0001 at default, classified "practically equivalent under the model" to the no-practice control A0. Its largest R30 across the EXP-002 smoke grid is 0.0066. Under power-law forgetting it is not at the floor (R30 0.111). As a "spaced repetition" comparator it is a strawman under exponential forgetting. | J-0005 to J-0007 |
| DG-4 Overload | K = 100 items, 672 reviews in 56 days, h0 = 1 day: round-robin (A1) revisits each item about every 7 days, when its recall is near 0 (success rate 0.064). Easiest-first (A2) concentrates on about half of the items (coverage 0.529, success rate 0.709) and keeps those alive. The primary contrast is therefore dominated by "concentrate on a subset versus spread too thin", not by streak timing. | J-0005, J-0007 |
| DG-5 EXP-002 floor rule | The preregistered rule "uninformative (floor) if mean R30 in A1 and A2 are both below 0.02" flags 0 of 27 smoke cells, although A1 alone is below 0.02 in 12 cells. | J-0006 |

## 2. Proposed amendments (owner's decision)

- **AP-1 Leave the floor regime (DG-1, DG-4).** Recalibrate the load before the freeze with an outcome-blind criterion stated in advance and applied to the controls only, for example: "at default parameters, smoke-seed mean R30 of A1 lies between 0.2 and 0.8 and A0 is not the only arm above 0.02". Candidate levers: fewer items (K), a longer median initial half-life h0 (and an EXP-002 grid centred on it), or a larger budget M. The AI has not searched these values, to avoid tuning on the primary contrast; it can run a control-only calibration on smoke seeds if the owner asks.
- **AP-2 Redefine A3 as threshold-based spaced repetition (DG-3).** For example: an item is due when its estimated recall falls to or below a target r* (for instance 0.9); due items are reviewed first, ordered by estimated recall closest to r* from below; remaining slots go to the items with the lowest estimated recall above a floor. Any choice must be fixed before the freeze. Otherwise A3 risks being a strawman comparator.
- **AP-3 Replace or supplement weakest-decile R30 (DG-2).** For example, the proportion of items with R30 of at least 0.5, or the 10th percentile of item log half-life. Keep weakest-decile R30 only if AP-1 removes the floor.
- **AP-4 EXP-002 floor rule (DG-5).** Change "both A1 and A2 below 0.02" to "either A1 or A2 below 0.02", or define it on A1 (the baseline) alone.
- **AP-5 Multiplicity wording.** Protocol section 6 asks for "Holm-adjusted intervals". The implementation reports Holm-adjusted bootstrap p-values with unadjusted 95% and 90% intervals (D-007 item 6). Proposed wording: "Holm-adjusted p-values (percentile bootstrap) for the secondary contrasts; intervals unadjusted and labelled as such". Alternative: Bonferroni-level intervals (level 1 - 0.05/m).
- **AP-6 Confirm the implementation readings in D-007** (scheduler belief uses the cell's population parameters; common random numbers per (day, item); within-day order; final-streak and weakest-decile definitions; gate rule).
- **AP-7 Planning values that need no change.** The assumed SD of the paired difference (0.05) is of the right order: measured 0.0207 at default (n = 1,000), 0.013 to 0.079 across the EXP-002 smoke cells (n = 100 per cell) and 0.014 to 0.027 across the EXP-003 variants. Projected 95% half-widths at the planned sizes: about 0.0013 (EXP-001, n = 1,000) and at most about 0.0069 (EXP-002 and EXP-003, n = 500 per cell), all well below the SESOI 0.02. The 0.3 trigger of protocol section 6 was not reached. Five master seeds are adequate; these SDs may change if AP-1 or AP-2 is adopted, and the smoke runs should then be repeated.

## 3. Runtime (planning values in EXP protocols section 8)

Measured on the Apple M1 Pro under heavy concurrent load from other sessions (load average 25 to 80 on 10 cores during the runs), single process: 2.6 to 9.4 ms per learner-arm (5.4 ms for the full-size EXP-001 matrix on smoke seeds: 4,000 learner-arms in 21.6 s, peak RSS 79.5 MB). Projected wall time: EXP-001 about 10 to 40 s; EXP-002 (54,000 learner-arms) about 2.3 to 8.5 minutes; EXP-003 (12,000) about 0.5 to 1.9 minutes; full matrix about 3 to 11 minutes plus report generation (2 s for the 27-cell smoke report). All are far below the hard caps (2 h, 4 h, 2 h). No change proposed.

## Outcome (2026-11-24)

The owner approved, and protocol 1.0 section 14 applies: AP-1 (via the Duolingo fit of h0 and the control-only floor check, K = 200), AP-2 (threshold A3, r* = 0.9), AP-5 (Holm wording) and the disclosure. AP-3, AP-4 and AP-6 were not in the approved list and are not applied. AP-7 needed no change. See `research/freeze_record.md`.
