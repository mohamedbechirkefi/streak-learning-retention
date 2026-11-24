<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# EXP-003 protocol: timing versus item selection, and model-form sensitivity

| Field | Value |
|---|---|
| Experiment ID | EXP-003 |
| Version | 0.1-draft, 2026-11-24 |
| Status | planned (protocol draft, awaiting owner freeze) |
| Parent protocol | `research/protocol.md` v0.1-draft (P§N) |
| Depends on | EXP-001 implementation and invariant tests |
| Protocol hash | none until the owner freezes it |
| Role | contains the sensitivity analysis that can invalidate the main interpretation (P§9 item 1) |

## 1. Precise question

(a) How much of the R30 difference between A2 Streak and A1 Fixed is due to daily timing and how much to easiest-first item selection? (b) Does the A2 versus A1 difference survive a flat (difficulty-independent) gain rule and a power-law forgetting curve?

## 2. Mechanism and rationale

The expected streak penalty in EXP-001 rests on two assumptions: that reviewing well-known items yields little durability gain (difficulty-dependent gain), and the exponential forgetting form. The spacing literature (Cepeda et al. 2006) supports spacing benefits but does not fix the functional form of the model; the FSRS documentation uses a power-law curve. If the penalty disappears when the assumptions change, the conclusion must be stated as conditional on them.

## 3. Competing explanations

- Timing-only: daily practice itself (more, shorter sessions) changes retention regardless of selection.
- Selection-only: neglect of weak items drives the gap regardless of timing.
- Model artefact: the gap exists only under the difficulty-dependent gain.

## 4. Hypotheses and disconfirmation

Policy cells (timing × selection): {daily, 3 per week} × {round-robin, easiest first, most due first}. A1 = (3 per week, round-robin), A2 = (daily, easiest first), A3 = (daily, most due first).

Model variants: {exponential, power-law} × {difficulty-dependent gain, flat gain}.

- H-sel: within each timing level, R30(easiest first) - R30(round-robin) ≠ 0 (two-sided; expected negative under difficulty-dependent gain).
- H-time: within each selection rule, R30(daily) - R30(3 per week) ≠ 0 (two-sided, no expected direction).
- **H-inv (invalidation test):** under flat gain (each forgetting form), E[R30(A2) - R30(A1)] ≠ 0. If the 90% interval lies inside ±0.02 or the 95% interval lies entirely above 0 under flat gain, the EXP-001 interpretation is reported as dependent on the difficulty-dependent gain assumption.

## 5. Estimand

Mean paired differences in R30 for the contrasts above, in each of the four model variants; main effects and the timing × selection interaction (difference of differences) in the 2 × 3 design.

## 6. Unit, scope and variables

- Unit: synthetic learner, run under all 6 policy cells and all 4 model variants (common random numbers).
- Independent: timing, selection, forgetting form, gain rule.
- Dependent: R30 primary; secondary metrics of P§5.
- The scheduler's belief model stays at the default (exponential, difficulty-dependent) in all variants, so the variants also test robustness to scheduler misspecification.

## 7. Sampling, seeds and sample size

Master seeds 1 to 5, 100 learners each (500 learners per condition). Planning half-width about 0.0044 at sd 0.05.

## 8. Fixed compute budget

12,000 learner-arm simulations; planning estimate under 15 minutes; hard cap 2 hours.

## 9. Metric formulas and units

- Power-law form: p(t) = (1 + 3 (t - s) / h)^(-0.5).
- Flat gain: h ← h · 1.85 on success.
- Interaction: [R30(daily, easiest) - R30(daily, round-robin)] - [R30(3 per week, easiest) - R30(3 per week, round-robin)].
- Others as P§5.

## 10. Uncertainty method

Stratified percentile bootstrap, 10,000 resamples, 95% and 90% intervals for each contrast in each model variant. Holm adjustment across the planned contrasts within each model variant; H-inv is reported unadjusted as a preregistered single test per forgetting form.

## 11. Exclusion and stopping rules

As P§7. Fixed design, single run.

## 12. Anticipated failure modes

Power-law forgetting decays slowly at long delays, which may compress R30 differences towards the top; reported with AUC-R and weakest-decile R30 alongside.

## 13. Sensitivity tests

This experiment is itself the sensitivity analysis. Residual exclusion applied as in P§7.

## 14. Reproducibility commands (planned for M2)

```
uv run python -m streak.cli run --experiment EXP-003 --config research/experiments/EXP-003/config.json
uv run python -m streak.cli report --experiment EXP-003
```
