<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# EXP-001 protocol: streak-driven versus fixed practice at matched minutes

| Field | Value |
|---|---|
| Experiment ID | EXP-001 |
| Version | 1.0, 2026-11-24 (frozen) |
| Status | frozen (owner-approved 2026-11-24), not yet run |
| Parent protocol | `research/protocol.md` v1.0 (sections cited as P§N) |
| Protocol hash | SHA-256 recorded in `research/experiment_registry.csv` and `research/freeze.json` |
| Type | confirmatory after freeze; simulation of synthetic learners |

## 1. Precise question

At default model parameters and identical total practice minutes, does streak-driven scheduling (A2) produce a different mean expected recall 30 days after practice ends (R30) than a fixed three-sessions-per-week schedule (A1)?

## 2. Mechanism and rationale

Retrieval practice strengthens memory (Roediger and Karpicke 2006), spacing improves long-term retention (Cepeda et al. 2006), and recall decays with time since last exposure (Ebbinghaus curve, replicated by Murre and Dros 2015; half-life model of Settles and Meeder 2016). A streak rewards being active every day, not the memory value of what is practised. If a streak-maintaining learner fills short daily sessions with items that are already well known (quick wins), each review then adds little durability under a desirable-difficulty update, and less-known items are neglected. Activity can therefore rise while retention stays flat or falls. Streaks are known to motivate continued engagement as a goal in itself (Silverman and Barasch 2022); this experiment holds time fixed and asks only about the retention value of the time spent.

## 3. Competing explanations

- Any difference may come from timing (daily versus 3 per week) rather than item selection: addressed by EXP-003.
- Any difference may be produced by the assumed difficulty-dependent gain: addressed by EXP-003 (flat gain).
- Any difference may be specific to the default parameters: addressed by EXP-002.
- Unspent minutes (residual) could favour one arm: residual reported and used in a sensitivity exclusion.

## 4. Hypotheses and disconfirmation

- H0: E[Δ] = 0, with Δ_l = R30_l(A2) - R30_l(A1).
- H1: E[Δ] ≠ 0 (two-sided; expected direction negative).
- Contradicts the expected direction: 95% interval entirely above 0, or 90% interval inside (-0.02, +0.02) (practical equivalence under the model).
- Supports the expected direction with practical relevance: 95% interval entirely below -0.02.
- Any other outcome is reported as "statistically detectable but below the SESOI" (interval excludes 0 but crosses ±0.02) or "inconclusive" (interval includes 0 and equivalence is not shown).

## 5. Estimand

Population mean, over the synthetic learner distribution of P§2, of the within-learner paired difference in R30 between A2 and A1.

## 6. Unit, scope and variables

- Experimental unit: one synthetic learner (P§6). Simulation scope: the model of P§2 at default parameters.
- Independent variable: scheduling arm (A0, A1, A2, A3).
- Dependent variables: R30 (primary); R1, R7, R90, AUC-R, minutes, residual, reviews, active days, streaks, missed days, practice success rate, item coverage, weakest-decile R30, activity-retention association (secondary, P§5).
- Treatment: A2 Streak. Control: A1 Fixed (primary baseline). Other arms: A3 Spaced (comparator), A0 NoPractice (negative control).

## 7. Sampling, seeds and sample size

Confirmatory master seeds 1 to 5, 200 learners each, 1,000 learners per arm, all four arms on every learner with common random numbers. Rationale in P§6 (planning: interval half-width about 0.003 at an assumed standard deviation 0.05).

## 8. Fixed compute budget

4,000 learner-arm simulations, single process, expected under 10 minutes on the M1 Pro (planning estimate; measured runtime and peak memory recorded in the run manifest). Hard cap: 2 hours wall clock; exceeding it stops the run and is reported.

## 9. Metric formulas and units

- p_i(t) = 2^(-(t - s_i) / h_i) (default exponential form).
- R30 = (1/K) Σ_i p_i(T + 30), T = 56, K = 200 (P§14.8); unitless proportion.
- Δ_l as above; d_z = mean(Δ) / sd(Δ).
- Other metrics as in P§5.

## 10. Uncertainty method

Stratified percentile bootstrap over learners within master seeds, 10,000 resamples, 95% and 90% intervals, bootstrap seed 20261124. Per-seed means, d_z and raw distributions reported. Secondary contrasts: Holm-adjusted bootstrap p-values within the cell, intervals unadjusted (P§14.6).

## 11. Exclusion and stopping rules

P§7: no outcome-based exclusion; residual above 34 slots flagged and excluded only in a sensitivity analysis; errors recorded; analysis halts if more than 1% of learner-arms fail. Fixed n, single run, no optional stopping.

## 12. Anticipated failure modes

- Budget not conserved or cap violated (caught by invariant tests).
- A2 and A3 indistinguishable because the estimated ranking saturates (all estimates near 1 or near 0); checked in smoke on smoke seeds.
- R30 floor effects (near 0 for all arms) making differences uninformative; checked in smoke; if present, the owner is asked before the freeze whether to change the delay or parameters.

## 13. Sensitivity tests

Residual-based exclusion (P§7). Model-form and parameter sensitivity are separate registered experiments (EXP-002, EXP-003).

## 14. Reproducibility commands (planned for M2)

```
uv sync --frozen
uv run python -m streak.cli run --experiment EXP-001 --config research/experiments/EXP-001/config.json
uv run python -m streak.cli report --experiment EXP-001
```

Outputs (planned): `research/experiments/EXP-001/metrics.csv`, `run_manifest.json`, `figures/`, raw per-learner results under `results/raw/EXP-001/` (regenerated, not committed).

## Amendments before freeze (owner-approved 2026-11-24, round 2)

Parent protocol section 14 governs; summary for this experiment:

- **Real data.** h0 = 67.59 days, fitted to the Duolingo traces (Settles and Meeder 2016, CC BY-NC 4.0) on the fit user split by the method of P§14.2 (journal J-0009), replaces the planning value of 1 day. K = 200 items, set by the control-only floor check of P§14.3 (A0 and A1 only, smoke seeds; J-0010), replaces K = 100. The held-out user split gives the preregistered second test of P§14.4, evaluated once after the freeze; it does not test this experiment's hypotheses.
- **A3.** Threshold-based spaced repetition (P§14.5, r* = 0.9) replaces "most due first".
- **Multiplicity wording.** P§14.6.
- **Disclosure.** A2 > A1 was seen on smoke seeds at the draft parameters before this freeze (P§14.7, with values and paths).
