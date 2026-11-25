<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Limitations and threats to validity (living document; updated in M4, 2026-11-25)

This file lists limitations known by design and, since M3, issues observed in the confirmatory runs (section "Observed in M3"). Section "Added in M4" records the interpretation-stage limits.

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

## Added in M4 (2026-11-25, interpretation and second review pass)
- **A2 is an extreme stylisation.** It always reviews the items it believes easiest. Its effect size is not an estimate for any real behaviour. The direction is not a pure artefact of coverage: in an exploratory run with K = 50, A2 covered 0.6726 of the items and the gap was still -0.2358 (J-0018).
- **"Streaks" versus selection.** Daily timing alone is retention-neutral at the SESOI (EXP-003). The retention cost belongs to easiest-first selection. Combined with easiest-first, daily timing is slightly but detectably worse (A2 - F-EASY -0.0110 to -0.0150), below the SESOI. Statements about "streaks" must name the selection rule.
- **Magnitude depends on unvalidated scales.** K = 200 was set by a ceiling rule on A1, and the gap varies non-monotonically with K (exploratory: -0.2323 to -0.3164). The absolute gap shrinks with slower forgetting (exploratory: -0.0342 at 16 times the fitted h0), while the share of A1's gain that A2 recovers stays near 0.19. The held-out test does not validate the forgetting scale.
- **Sign reversal in the floor regime.** At the draft parameters (near-total forgetting) A2 beat A1 (+0.0801, smoke seeds). That is a regime of the model where the divergence does not occur. The decision to leave that regime was taken with these values visible. The parameter rules used control arms only.
- **A3 equivalence is conditional.** A3 < A1 at h0 = 33.8 days (EXP-002) and at K = 400 (exploratory, -0.0621).
- **Non-independent confirmations.** The EXP-002 cells share learners. The EXP-003 default variant reproduces the EXP-002 default cell exactly (-0.3089), since both use seeds 1 to 5 with 100 learners.
- **Agreement with prior work is by construction.** The model encodes the retrieval-practice and spacing assumptions, so agreement with those sources is not independent support.
- **External sources.** Settles and Meeder (2016) was read in full for the cited points. The other cited sources were read as abstracts only, and Ye et al. (2022) as metadata only (`literature_review.md`, section 4).
- **Provenance details.** Figure IDs repeat across experiments (the manuscript uses experiment-qualified copies). The `generated/frozen_analysis.json` files record an absolute local result path. Neither affects any number.

## Ethics boundary
- No pressure-based or manipulative UX in the demo. Attention and user agency are outcomes to report, never targets to optimise.
