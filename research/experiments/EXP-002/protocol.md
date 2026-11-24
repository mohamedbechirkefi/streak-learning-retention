<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# EXP-002 protocol: when does the streak-retention gap appear? Robustness across forgetting parameters and availability

| Field | Value |
|---|---|
| Experiment ID | EXP-002 |
| Version | 0.1-draft, 2026-11-24 |
| Status | planned (protocol draft, awaiting owner freeze) |
| Parent protocol | `research/protocol.md` v0.1-draft (P§N) |
| Depends on | EXP-001 implementation and invariant tests (not on EXP-001 results; the grid is fixed now) |
| Protocol hash | none until the owner freezes it |

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
- Independent variables: arm (A0 to A3); h0 in {0.5, 1, 2} days; a in {1.5, 2.5, 4}; q in {0.7, 0.85, 1.0}.
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
