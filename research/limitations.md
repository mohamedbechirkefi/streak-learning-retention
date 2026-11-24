<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Limitations and threats to validity (living document, M0 draft)

This file lists limitations known by design and, since M3, issues observed in the confirmatory runs (section "Observed in M3"). It is extended again in M4.

## Construct validity
- "Streak-driven scheduling" is one stylised policy (daily practice plus easiest-first selection). It is not a model of any real product, and not a model of real learner motivation.
- Retention is the model's expected recall probability, not a measured test score of a human.
- Practice time is held fixed by design. Streaks may change how much people practise (Silverman and Barasch 2022 report engagement effects); this project deliberately does not model that, so it cannot say whether streaks help or hurt learning overall in practice.

## Internal validity
- Results depend on the assumed memory model (forgetting form, update rule, failure rule). EXP-003 tests the update rule and forgetting form; other assumptions (item independence, no interference, no within-day decay) remain.
- A1 and A2 differ in timing and selection; EXP-003 separates them.
- Carry-forward can leave unspent minutes; the residual is reported and used in a sensitivity exclusion.

## Statistical validity
- Synthetic learners are independent by construction; intervals describe simulation uncertainty given the model, not uncertainty about real populations.
- Planning values (SESOI 0.02, sd 0.05) are not measured.

## External validity
- No human data. No claim about real human learning efficacy, any commercial application, or causal human behaviour can follow from these simulations.
- Parameter ranges (EXP-002) are planning choices, not calibrated to real learners (D-003).

## Observed in M3 (2026-11-25, confirmatory runs)
- **Forgetting form against real data (negative result, P§14.4, J-0014).** On held-out Duolingo first-repeat data the exponential form (h0 fitted on the fit split) has lower log-likelihood per trial than a constant-recall baseline (-0.3865 versus -0.3352), and the power-law form (-0.3710) is better supported than the exponential form. Observed recall falls only from 0.904 (1 to 2 days) to 0.872 (32 to 90 days), far flatter than either form predicts with σ = 0.583. The calibrated h0 = 67.59 days therefore anchors only an order of magnitude; the simulated time scale is not validated by these data.
- **The size of the A2 gap is driven by item selection, not timing (EXP-003).** Easiest-first selection concentrates practice on about 17% of the K = 200 items (EXP-001 coverage 0.172). The gap magnitude depends on that stylised rule and on K relative to the 672-slot budget; neither is calibrated to real learners.
- **Robustness is within the model only.** EXP-002 (27 cells) and EXP-003 (4 model variants) leave the gap negative everywhere tested, but every variant keeps the same item-independence, no-interference and scheduler-belief assumptions.
- **Main effects in EXP-003** use the conventional equal-weight marginal definition, an AI reading; the protocol names main effects without a formula.
- **Provenance.** The EXP-002 run manifest records `git_dirty = true` because records files (no code, config or protocol) were edited while it ran (D-016).

## Ethics boundary
- No pressure-based or manipulative UX in the demo. Attention and user agency are outcomes to report, never targets to optimise.
