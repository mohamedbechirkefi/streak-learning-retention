<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# STREAK research protocol

| Field | Value |
|---|---|
| Version | 0.1-draft |
| Date | 2026-11-24 |
| Status | **DRAFT, NOT FROZEN.** Awaiting owner review and freeze (gate G-FREEZE). No confirmatory run may start before the owner freezes this file and the EXP protocols and their hashes are recorded in `research/experiment_registry.csv`. |
| Protocol hash | none yet (assigned at freeze: SHA-256 of the frozen file) |
| Author role | Drafted by the AI assistant for owner review. The owner decides hypotheses, metrics and the freeze. |

Planning values in this document (default parameters, smallest effect size of interest, assumed standard deviation) are **planning proposals**, not measurements. They are labelled as such where they appear.

## 1. Research question

Master prompt section 10: *When can activity streaks diverge from knowledge retention in a learning model?*

Operational restatement: in a simulated population of learners with forgetting, retrieval practice, a fixed total practice time and stochastic day-to-day availability, does a streak-driven scheduling policy (practise every available day, favour items that are quick to succeed on) produce different long-term retention from a simple fixed practice schedule that spends exactly the same number of practice minutes, and under which forgetting parameters and model assumptions does any difference appear, vanish or reverse?

"Diverge" means: a policy scores higher on activity measures (active days, streak length) while scoring equal or lower on retention measured after held-out delays.

## 2. Formal model (synthetic, labelled simulation)

All time is in days. Each learner studies a curriculum of K items.

**Memory state.** Item i of learner l has a half-life h (days) and a time of last exposure s. True recall probability at time t:

- Exponential form (default, after the half-life regression model of Settles and Meeder 2016): p(t) = 2^(-(t - s) / h).
- Power-law form (sensitivity, shape inspired by the FSRS forgetting curve documentation): p(t) = (1 + 3 (t - s) / h)^(-0.5). The constant 3 = 2^(1/0.5) - 1 makes p equal 0.5 at t - s = h in both forms.

**Initial study.** At day 0 every item is studied once (identical for all arms, not counted in the practice budget): s = 0, h = h0 · u_i · θ_l, where u_i ~ LogNormal(0, 0.5²) is item difficulty and θ_l ~ LogNormal(0, 0.3²) is learner ability.

**Review.** A review at time t is a retrieval attempt. It succeeds with probability p(t) (Bernoulli draw). Then s = t and:

- success, difficulty-dependent gain (default): h ← h · (1 + g_min + a · (1 - p(t))), with g_min = 0.1, a = 2.5 (planning values). Reviewing an item that is already almost certainly recalled gives little gain; this encodes the desirable-difficulty and spacing assumption.
- success, flat gain (sensitivity): h ← h · (1 + g_flat), g_flat = g_min + a · 0.3 = 0.85, equal to the default gain at p = 0.7.
- failure (feedback then relearning): h ← max(h_min, b · h), b = 0.6, h_min = 0.25.

Each item is reviewed at most once per day; reviews within a day happen at integer time t = d.

**Time budget.** Each review costs one slot of 0.5 minutes (integer arithmetic on slots). Practice horizon: days 1 to T = 56. Total budget per learner M = 672 slots (336 minutes, on average 6 minutes per calendar day). Daily cap: 60 slots (30 minutes).

**Availability.** Each day d in 1..T the learner is available with probability q (default 0.85), i.i.d.; unavailable days cannot hold practice. The availability sequence is drawn once per learner and shared by all arms (common random numbers).

**Carry-forward rule (all arms).** Slots planned for a day that is unavailable, or left unspent because of the cap, are added to the next available day. For daily arms this is simply the next available day. For A1 Fixed, a missed scheduled session is made up on the next available day, whether or not it is a scheduled weekday (a "make-up day"), and that day's slots are added on top of any session already scheduled for it, up to the cap. Slots still unspent at the end of day T are the residual r. Conservation: spent + r = M exactly.

**Scheduler's belief.** Policies that rank items use an estimate of p computed with population-median parameters (θ = 1, u = 1) and the default exponential, difficulty-dependent model, updated with the observed review outcomes. The scheduler never sees the true state. Under model-form variants, the scheduler's belief is deliberately left misspecified.

## 3. Arms (EXP-001)

| Arm | Timing | Item selection | Role |
|---|---|---|---|
| A0 NoPractice | none after day 0 (M = 0) | none | negative control (zero practice minutes, not matched) |
| A1 Fixed | 3 fixed weekdays per week (days with d mod 7 in {1, 3, 5}), 28 slots per scheduled session (24 sessions = 672 slots) | round-robin in a fixed item order | **primary baseline (simplest comparator: no learner model, no adaptivity)** |
| A2 Streak | every available day, 12 slots per day plus carry-forward | easiest first: highest estimated recall probability first | treatment: streak-maintenance with quick wins |
| A3 Spaced | every available day, 12 slots per day plus carry-forward | most due first: lowest estimated recall probability first | comparator: spaced repetition by estimated recall |

A2 and A3 have identical timing and therefore identical activity counts and streaks; they differ only in item selection. A1 and A2 differ in both timing and selection; EXP-003 decomposes that difference.

## 4. Hypotheses (primary)

Let R30 be the primary metric (section 5) and, for each learner l, Δ_l = R30_l(A2 Streak) - R30_l(A1 Fixed), computed on the same learner, availability sequence and outcome random stream.

- **H0:** E[Δ] = 0.
- **H1 (two-sided):** E[Δ] ≠ 0. The preregistered expected direction is Δ < 0 (streak-driven scheduling retains less at matched minutes), but the test is two-sided.
- **Smallest effect size of interest (SESOI):** 0.02 in R30 (two percentage points of expected recall). Planning proposal, owner to confirm.
- **Decision rule.** Reject H0 if the 95% bootstrap confidence interval of E[Δ] excludes 0. Call the difference practically relevant only if the interval also lies entirely beyond -0.02 or +0.02. Call the arms practically equivalent under the model only if the 90% interval lies inside (-0.02, +0.02). Otherwise the result is inconclusive at the SESOI. Non-significance is never reported as equivalence.
- **What contradicts the expected direction:** a 95% interval entirely above 0, or a 90% interval inside the equivalence bounds.

## 5. Metrics

**Primary metric: R30.** Mean true recall probability over all K items, 30 days after the end of the practice horizon (t = T + 30 = 86), computed analytically from the true memory state (expected recall, a proportion in [0, 1]; higher is better). Justification: retention after a held-out delay is the construct the question opposes to activity; the analytic expectation removes test-sampling noise without changing the estimand; 30 days is long enough that short-term maintenance cannot mask forgetting and short enough to lie in the range studied by Cepeda et al. (2006).

**Secondary metrics.**

| Metric | Definition | Unit |
|---|---|---|
| R1, R7, R90 | as R30 at delays of 1, 7 and 90 days after T | proportion |
| AUC-R | mean of R over delays 0 to 90 days (daily grid) | proportion |
| Minutes spent | slots spent × 0.5 | minutes |
| Residual | unspent slots r at end of T | slots |
| Reviews | number of review events | count |
| Active days | days with at least one review | days |
| Longest streak, final streak | longest and final run of consecutive active days | days |
| Missed days | (a) unavailable days (exogenous, equal across arms); (b) available days without practice (policy-driven) | days |
| Practice success rate | successful reviews / reviews | proportion |
| Item coverage | items reviewed at least once in 1..T | proportion of K |
| Weakest-decile R30 | mean R30 of the 10% of items with lowest R30 for that learner | proportion |
| Activity-retention association | within-arm Spearman correlation across learners between active days and R30 | coefficient |

## 6. Design, units, seeds and sample size

- **Experimental unit:** one synthetic learner (parameters, item difficulties, availability sequence and outcome random stream). All arms are run on every learner (within-learner paired design, common random numbers).
- **Seeds:** confirmatory master seeds 1, 2, 3, 4, 5; each master seed generates an independent population of learners via NumPy `SeedSequence` spawning. Smoke and development seeds are 9001 to 9005 and are never pooled with confirmatory results. Confirmatory seeds are not run before the freeze.
- **Sample size (EXP-001):** 5 master seeds × 200 learners = 1,000 learners per arm. Rationale (planning proposal): with an assumed standard deviation of the paired difference of 0.05, the 95% interval half-width is about 1.96 × 0.05 / sqrt(1000) ≈ 0.003, far below the SESOI of 0.02; even at a standard deviation of 0.15 it is about 0.009. Compute cost is negligible, so n is not the binding constraint. The smoke run measures the actual standard deviation on smoke seeds only; if it exceeds 0.3, the owner is asked whether to raise n before the freeze.
- **Uncertainty method:** 95% (and 90% for equivalence) percentile bootstrap of the mean paired difference, 10,000 resamples, resampling learners within each master seed (stratified), bootstrap seed fixed and recorded. Also reported: per-master-seed mean differences (5 values), the paired effect size d_z, and the raw distribution of Δ (histogram and quantiles).
- **Multiplicity:** one primary contrast (A2 vs A1). Secondary pairwise contrasts on R30 (A3 vs A1, A2 vs A3, and each practice arm vs A0) are reported with Holm-adjusted intervals and labelled secondary. Secondary metrics are descriptive.
- **Stopping rule:** fixed sample size; the confirmatory matrix is run once in full. No optional stopping, no re-running with new seeds to change a result.

## 7. Inclusion, exclusion and failure handling

- All learners are included in the primary analysis (no outcome-based exclusion).
- A learner-arm whose residual r exceeds 5% of M (34 slots) is flagged. The primary analysis keeps it; a sensitivity analysis excludes all flagged learners (from every arm, to keep pairing).
- A run that raises an error or fails schema validation is recorded with its error in the run manifest and the journal; it is never dropped silently. If more than 1% of learner-arms fail, analysis stops and the cause is investigated and reported before any result is interpreted.

## 8. Controls and verification (before any confirmatory run)

- **No-practice control** (A0): recall equals the closed form from the initial state, zero reviews, zero minutes.
- **Forgetting curve bounds:** 0 ≤ p ≤ 1, p = 1 at zero delay, p non-increasing in delay, p = 0.5 at delay h (both forms).
- **Scheduling:** A1 practises only on its scheduled or make-up days; A2 and A3 practise on every available day while budget remains; A2 picks the highest and A3 the lowest estimated recall; at most one review per item per day.
- **Time-budget conservation:** spent + residual = M for every learner-arm; daily cap never exceeded; no practice on unavailable days.
- **Determinism:** identical seeds and config give byte-identical result files on the same platform.
- **Hand-computed golden examples** for one item and one learner.

## 9. Sensitivity analyses (at least one could invalidate the main interpretation)

1. **Update-rule sensitivity (EXP-003, the potentially invalidating test).** Under the flat-gain rule, reviewing easy items is no longer penalised by the model. If the A2 vs A1 difference in R30 disappears (90% interval inside ±0.02) or reverses under flat gain, then any divergence found in EXP-001 is a consequence of the desirable-difficulty assumption, not of streak-driven timing as such, and must be reported that way.
2. **Timing versus selection decomposition (EXP-003).** A 2 × 3 factorial of timing (daily, 3 per week) by selection (round-robin, easiest first, most due first) separates the effect of daily activity from the effect of item choice.
3. **Forgetting-form sensitivity (EXP-003).** Exponential versus power-law forgetting.
4. **Parameter robustness (EXP-002).** Grid over median initial half-life h0, gain a and availability q.
5. **Residual exclusion** (section 7).

## 10. Experiment plan and matrices

| ID | Purpose | Matrix | Learner-arm simulations |
|---|---|---|---|
| Smoke | toolchain, invariants, runtime, variance check (exploratory) | 4 arms × smoke seeds 9001 to 9005 × 20 learners, default parameters | 400 |
| EXP-001 | primary comparison at default parameters | 4 arms × 5 seeds × 200 learners | 4,000 |
| EXP-002 | robustness across forgetting parameters and availability ("when") | 27 cells (h0 in {0.5, 1, 2} days × a in {1.5, 2.5, 4} × q in {0.7, 0.85, 1.0}) × 4 arms × 5 seeds × 100 learners | 54,000 |
| EXP-003 | mechanism decomposition and model-form sensitivity | 6 policy cells × 4 model variants (exponential or power-law × difficulty-dependent or flat gain) × 5 seeds × 100 learners | 12,000 |

Fixed parameters for all experiments unless varied: K = 100, T = 56, M = 672 slots, slot = 0.5 minute, daily cap 60 slots, g_min = 0.1, a = 2.5, b = 0.6, h_min = 0.25, h0 = 1 day, q = 0.85, retention delays {1, 7, 30, 90} days.

Each experiment has its own protocol in `research/experiments/EXP-NNN/protocol.md`.

## 11. Confounders and threats (summary; detailed in `research/limitations.md`)

- The result is model-dependent: update rule, forgetting form and the scheduler's belief model are assumptions.
- A1 and A2 differ in two factors at once (timing and selection); EXP-003 addresses this.
- Matched minutes is the design control; the residual is reported because carry-forward can leave unspent time.
- The A2 "easiest first" rule is one stylised operationalisation of streak-driven behaviour, not a model of any real product or of real learner motivation. No behavioural or motivational effect of streaks (for example, Silverman and Barasch 2022) is modelled: time spent is held fixed by design.

## 12. Reproducibility commands (planned, implemented in M2)

```
uv sync --frozen
uv run python -m streak.cli test
uv run python -m streak.cli smoke
uv run python -m streak.cli run --experiment EXP-001
uv run python -m streak.cli report --experiment EXP-001
```

These commands do not exist yet (M0). They will be recorded with their actual outputs when implemented.

## 13. Amendments

None. Any amendment after the freeze is dated, justified, and kept separate from the frozen analysis; results that depend on it are labelled exploratory.
