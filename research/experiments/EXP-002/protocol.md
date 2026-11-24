<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# EXP-002 protocol: when does the streak-retention gap appear? Robustness across forgetting parameters and availability

| Field | Value |
|---|---|
| Experiment ID | EXP-002 |
| Version | 1.0, 2026-11-24 (frozen) |
| Status | frozen (owner-approved 2026-11-24), not yet run |
| Parent protocol | `research/protocol.md` v1.0 (P§N) |
| Depends on | EXP-001 implementation and invariant tests (not on EXP-001 results; the grid is fixed now) |
| Protocol hash | SHA-256 recorded in `research/experiment_registry.csv` and `research/freeze.json` |

## 1. Precise question

Across a fixed grid of median initial half-life h0, success gain a and daily availability q, in which cells does R30 under A2 Streak differ from A1 Fixed at matched minutes, and is the sign of the difference consistent across the grid?

## 2. Mechanism and rationale

The question asks "when". Faster forgetting (small h0) raises the value of reviewing weak items; a larger gain a strengthens the desirable-difficulty penalty on easy reviews; lower availability q shortens streaks for every daily arm and shifts minutes through carry-forward. Each could enlarge, shrink or reverse the gap.

## 3. Competing explanations

A gap that only appears at extreme values would indicate a boundary phenomenon of the model rather than a general property. A gap driven by residual time (low q) would be a budget artefact; residual is reported per cell.

## 4. Hypotheses and disconfirmation

- Per cell c: H0_c: E[Δ_c] = 0; H1_c: E[Δ_c] ≠ 0, Δ = R30(A2) - R30(A1).
- Grid-level descriptive hypothesis (expected, not tested for significance): the sign of E[Δ_c] is negative in all 27 cells.
- Disconfirms grid-level robustness: any cell whose 95% interval lies entirely above 0, or more than one third of cells (9 or more) practically equivalent (90% interval inside ±0.02).

## 5. Estimand

For each cell, the mean paired difference in R30 between A2 and A1; and the count of cells by outcome category (relevant negative, relevant positive, equivalent, inconclusive).

## 6. Unit, scope and variables

- Unit: synthetic learner. Scope: model of P§2.
- Independent variables: arm (A0 to A3); h0 in {33.8, 67.59, 135.18} days (0.5, 1 and 2 times the fitted h0, P§14.2 and P§14.8); a in {1.5, 2.5, 4}; q in {0.7, 0.85, 1.0}.
- Dependent: R30 (primary per cell), secondary metrics of P§5.
- Treatment A2, control A1; A3 and A0 retained.

## 7. Sampling, seeds and sample size

Master seeds 1 to 5, 100 learners each per cell (500 learners per cell per arm). Learner draws are shared across cells for the same seed and learner index (common random numbers across the grid). Rationale: at an assumed standard deviation of 0.05 the half-width is about 0.0044 per cell (planning value), still well below the SESOI.

## 8. Fixed compute budget

54,000 learner-arm simulations; planning estimate under 1 hour; hard cap 4 hours.

## 9. Metric formulas and units

As P§5 and EXP-001 §9, with p computed using the cell's h0 and a.

## 10. Uncertainty method

Per cell: stratified percentile bootstrap (10,000 resamples), 95% and 90% intervals. Multiplicity: 27 cells; per-cell intervals are reported unadjusted and labelled per-cell, plus a Holm-adjusted classification across the 27 cells for the "relevant" category. The result is shown as a heat map of mean Δ with interval-based category markers, plus the full table.

## 11. Exclusion and stopping rules

As P§7, applied per cell. Fixed grid, single run, no cell added or removed after seeing results.

## 12. Anticipated failure modes

Floor effects at h0 = 0.5 with a = 1.5 (R30 near 0 in all arms), making the comparison uninformative; such cells are reported as "uninformative (floor)" if mean R30 in A1 and A2 are both below 0.02, a rule fixed now.

## 13. Sensitivity tests

Residual exclusion per cell. Report whether the q = 1.0 cells (no carry-forward) agree in sign with the others.

## 14. Reproducibility commands (planned for M2)

```
uv run python -m streak.cli run --experiment EXP-002 --config research/experiments/EXP-002/config.json
uv run python -m streak.cli report --experiment EXP-002
```

## Amendments before freeze (owner-approved 2026-11-24, round 2)

Parent protocol section 14 governs; summary for this experiment:

- **Real data.** h0 = 67.59 days, fitted to the Duolingo traces (Settles and Meeder 2016, CC BY-NC 4.0) on the fit user split by the method of P§14.2 (journal J-0009), replaces the planning value of 1 day. K = 200 items, set by the control-only floor check of P§14.3 (A0 and A1 only, smoke seeds; J-0010), replaces K = 100. The held-out user split gives the preregistered second test of P§14.4, evaluated once after the freeze; it does not test this experiment's hypotheses.
- **A3.** Threshold-based spaced repetition (P§14.5, r* = 0.9) replaces "most due first".
- **Multiplicity wording.** P§14.6.
- **Disclosure.** A2 > A1 was seen on smoke seeds at the draft parameters before this freeze (P§14.7, with values and paths).
- **Holm across cells.** The primary-contrast p-values are Holm-adjusted across the 27 cells; a cell is "relevant (Holm across cells)" only if its unadjusted 95% interval lies beyond ±0.02 and its Holm-adjusted p is below 0.05 (P§14.6; config flag `holm_primary_across_cells`). The floor rule of section 4 of this protocol is unchanged (proposal AP-4 was not in the approved list).
