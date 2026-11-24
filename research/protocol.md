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

Section 14 holds the amendments made before the freeze, on the owner's approvals. Where section 14 and sections 1 to 12 differ, section 14 governs. Any amendment after the freeze is dated, justified, and kept separate from the frozen analysis; results that depend on it are labelled exploratory.

## 14. Amendments before freeze (owner-approved 2026-11-24, round 2)

**Authority.** `_shared/owner-approvals-2026-11-24b.md` (coordinator file), sections 1 and 7. The owner answered "yes for all others" to the STREAK amendment proposals (first round, 2026-11-24) and "Approve all" to the second-round list (2026-11-24), which says for STREAK: adopt "the same Duolingo logs" only "if a licence recheck is clean", fallback "stay synthetic"; and the approved amendments "Move the parameters off the recall floor (fitted from Duolingo if the licence is clean). Replace the strawman arm A3 with a meaningful comparator under a stated rule. Fix the Holm wording. Disclose that A2 > A1 was seen." Proposals AP-3 (weakest-decile metric), AP-4 (EXP-002 floor rule) and AP-6 (D-007 readings) are not in that list and are not applied: the weakest-decile metric and the EXP-002 floor rule stay as written in sections 5 and EXP-002, and the D-007 implementation readings remain the AI's documented readings (decision log D-007).

This section was written, and committed, before any model was fitted to the real data (decision D-011). Values marked "fitted" are filled in afterwards by the method below, without changing the method.

### 14.1 Real data: licence check and role (amendment R2-1)

- **Dataset.** Duolingo half-life regression learning traces (Settles and Meeder 2016), Harvard Dataverse, doi:10.7910/DVN/N8XJME, file `settles.acl16.learning_traces.13m.csv.gz` (Dataverse file id 3091087, 379,004,009 bytes). Licence, read on 2026-11-24 from the Dataverse dataset API (`termsOfUse` field): "This work is released under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)." This clearly permits non-commercial research use with attribution, so the licence recheck is clean and the data is adopted.
- **Handling.** Downloaded by `scripts/download_duolingo.py` into `data/raw/` with SHA-256, size, URL and access date recorded in `data/manifest.json`. The file is larger than 20 MB and holds pseudonymous user ids at row level, so it is git-ignored and never committed; so is the processed form (`data/processed/`). Only aggregate counts and fitted values are committed.
- **Role.** The simulation stays the controlled part of the study. The real data (a) calibrates exactly one parameter, the median initial half-life h0, and (b) supplies a second, descriptive test of the forgetting model on held-out users (14.3). It never enters the simulated arms, the primary contrast or any secondary contrast.

### 14.2 Calibration of h0 (method fixed before fitting)

- **Observations used.** Rows that pass schema validation (all twelve columns present with the expected types; 0 <= p_recall <= 1; delta >= 0; 0 <= history_correct <= history_seen; 1 <= session_seen; 0 <= session_correct <= session_seen; p_recall equal to session_correct / session_seen within 0.001), that are first repeats (history_seen = 1: the word was seen exactly once before this session, the closest analogue of the model's single initial study at day 0), and whose delay delta / 86,400 lies in [1, 90] days (the model's daily resolution up to its longest retention delay). Exclusions are counted in this order: schema invalid, not a first repeat, delay below 1 day, delay above 90 days. Missing values are counted per column.
- **Split.** By user: a row belongs to the fit split if the first byte of SHA-256(user_id, UTF-8) is even, and to the held-out split otherwise. The fit uses the fit split only. The user id is used for nothing else and is not stored in the processed form.
- **Model.** Each row is session_correct successes out of session_seen trials with recall probability E[2^(-Δ/h)], Δ the delay in days, and log h ~ Normal(log h0, σ²) with σ = sqrt(σ_item² + σ_learner²) = sqrt(0.5² + 0.3²) ≈ 0.5831, the heterogeneity the simulation already assumes (P§2, planning values, not fitted). The expectation is computed with 40-node Gauss-Hermite quadrature. Exponential form only (the default true model).
- **Estimator.** Maximum likelihood of the binomial log-likelihood in log h0: a 121-point grid over h0 in [0.05, 1000] days, then golden-section refinement to a tolerance of 1e-6 in log h0 (`streak.duolingo.fit_h0`). A likelihood-ratio 95% interval is reported, labelled naive (it treats trials as independent). A maximum on a grid edge is reported as a failure of the method, not used.
- **Use.** The fitted h0, rounded to two decimal places (days), replaces the planning value 1 day in every config. The EXP-002 h0 axis becomes {0.5, 1, 2} times the fitted value, each rounded to two decimals. No other parameter changes because of the fit. The fit is journaled as exploratory.
- **Caveat stated in advance.** Duolingo session recall is in-session exercise accuracy of users of one product, not a free-recall test after a single study; the calibrated h0 anchors the model's time scale to a real order of magnitude, it does not make the synthetic learners real.

### 14.3 Floor check after the fit (control arms only, rule fixed before fitting)

Exploratory, on smoke seeds 9001 to 9005 with 200 learners each, at the fitted h0 and the other default parameters, running the arms A0 and A1 only (never A2 or A3, so the primary contrast is not computed): the parameters are off the recall floor if the mean R30 of A1 lies in [0.2, 0.8]. If it does, K = 100 stays. If it is below 0.2, K = 50 is checked; if it is above 0.8, K = 200 and then K = 400 are checked; the first K that meets the criterion is adopted. If none does, the item stops and is reported to the owner, and nothing is frozen. Results are journaled as exploratory.

### 14.4 Second test on real data (preregistered, evaluated once after the freeze)

On the held-out user split, never used to fit: h0 is fitted on the fit split by the 14.2 method for both the exponential and the power-law form, and on the held-out split the mean binomial log-likelihood per trial is reported for each form and for a constant-recall baseline (pooled fit-split recall), with a calibration table of observed versus predicted recall by delay bins [1, 2), [2, 4), [4, 8), [8, 16), [16, 32), [32, 90] days (`streak.duolingo.heldout_evaluation`). Reading, fixed now: the exponential model "describes the held-out first-repeat data better than the constant baseline" if its log-likelihood per trial is higher; the form with the higher held-out log-likelihood is reported as better supported, which informs how much weight the EXP-003 power-law variant deserves. This test is descriptive, does not test H1, is not run before the freeze, and is reported in the EXP-001 report and the manuscript as a check of the model's forgetting assumption on real data.

### 14.5 A3 replaced by a threshold-based spaced-repetition comparator (amendment R2-2)

The draft A3 ("lowest estimated recall first") reviewed items already lost (smoke DG-3). It is replaced, before any run of the new rule, by this stated rule, with selection id `due_threshold`:

- With the scheduler's belief p̂ (P§2), an item is **due** if p̂ <= r*, with r* = 0.9 (the example value of the owner-approved proposal AP-2, fixed now).
- Due items are reviewed first, in decreasing order of p̂ (the item closest to r* from below first, so salvageable items come before items that are already almost lost).
- If slots remain, the non-due items are reviewed in increasing order of p̂ (those closest to becoming due first).
- Ties: lower item index first. Timing is unchanged (every available day, 12 slots plus carry-forward), so A3 still has exactly the activity of A2.

The same selection replaces "most due first" in the EXP-003 cell F-DUE (3 per week, `due_threshold`). The old rule is kept in the code under its old id `most_due` for the record but is used by no arm.

### 14.6 Multiplicity wording (amendment R2-3)

Section 6 "Holm-adjusted intervals" is replaced by: for the secondary contrasts, Holm-adjusted two-sided percentile-bootstrap p-values (p = 2 · min(share of bootstrap means <= 0, share >= 0), capped at 1), adjusted within each cell (in EXP-003, within each model variant); the 95% and 90% intervals are unadjusted and labelled as such; the primary contrast is not in that family. In EXP-002 the primary-contrast p-values are Holm-adjusted across the 27 cells, and a cell is reported as "relevant (Holm across cells)" only if its unadjusted 95% interval lies beyond ±0.02 and its Holm-adjusted p is below 0.05.

### 14.7 Disclosure: A2 > A1 was seen before the freeze (amendment R2-4)

Exploratory smoke runs on seeds 9001 to 9005 (engine 1.0.1, commit dfa9dd4, draft parameters h0 = 1 day, draft A3) computed the primary contrast before this freeze. A2 minus A1 in R30 was positive: +0.0801 (95% interval 0.0788 to 0.0813, n = 1,000, `results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv`, journal J-0005); +0.0768 (n = 100, `results/exploratory/SMOKE-EXP-001/`, J-0004); in the EXP-002 smoke grid the mean difference was above 0 in 23 of 27 cells, range -0.0787 to +0.0920 (`results/exploratory/SMOKE-EXP-002/report/contrasts.csv`, J-0006); in the EXP-003 smoke variants +0.0768 (exponential, difficulty gain), +0.0848 (exponential, flat), +0.0245 (power, difficulty) and +0.0855 (power, flat) (`results/exploratory/SMOKE-EXP-003/report/contrasts.csv`, J-0007). These values came from the floor regime that this section removes, so they say little about the frozen design, but they were seen by the AI and are visible to the owner. The amendments above were justified by the control arms and the operationalisation (DG-1 to DG-5), not by the primary contrast, and no new smoke run of A2 was made before the freeze.
