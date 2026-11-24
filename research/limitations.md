<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Limitations and threats to validity (living document, M0 draft)

No results exist yet. This file lists limitations known by design; it will be extended with observed issues in M3 and M4.

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

## Ethics boundary
- No pressure-based or manipulative UX in the demo. Attention and user agency are outcomes to report, never targets to optimise.
