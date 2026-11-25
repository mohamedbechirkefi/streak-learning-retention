<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Second review pass: arguing against the preferred hypothesis

| Field | Value |
|---|---|
| Date | 2026-11-25 (M4) |
| Object | `research/paper/manuscript.md` version 0.9, the three experiment reports, the claims register |
| Preferred hypothesis under challenge | "At matched minutes, streak-driven scheduling lowers retention while raising activity" (EXP-001 H1, expected direction), and its M4 reading "the gap comes from item selection, not daily timing" |
| Reviewer | the AI research assistant, adversarially. This is internal quality control, not peer review. The owner reviews the outcome. |
| Outcome | 17 challenges. 12 hold fully or partly and led to revisions (manuscript version 1.0). 5 do not hold, with reasons. No frozen verdict changes. |

The pass looks for the strongest alternative readings, overgeneralisation, stale figures, leakage and missing failed runs. Each challenge is followed by its evidence, a judgement (holds, partly holds, does not hold) and the change made.

## A. Alternative readings of the main result

**C-1. The headline credits "streaks" with an effect that the streak itself does not have.**
- *Evidence.* EXP-003 shows that daily timing is practically equivalent to 3 per week in every selection rule and variant: the timing main effect is -0.0030 to -0.0051. A3 has exactly A2's streaks and retains as much as A1. The gap belongs to easiest-first selection.
- *Judgement.* Holds. The draft title "Streaks without retention" and the abstract's framing imply that streaks cost retention. In this model a streak is harmless unless the daily minutes go to already-known items.
- *Change.* New title and abstract built on the actual finding: activity counts and retention come apart because activity counts do not see which items are practised. Section 6.1 now says so.

**C-2. The divergence is built into the operationalisation, so the result is close to tautological.**
- *Evidence.* A2 is a deterministic "highest estimated recall first" rule with 12 slots a day for 200 items. It reviewed 0.172 of the items with a success rate of 0.987. Any rule that leaves 83% of the material untouched for 86 days will lose retention, whatever it is called.
- *Counter-evidence.* In the exploratory K = 50 run (J-0018), A2 covered 0.6726 of the items and still lost -0.2358. The per-learner association between A2 coverage and the gap in EXP-001 is weak (Spearman 0.206). So coverage is not the whole channel; repeatedly reviewing items that are already safe also wastes the budget.
- *Judgement.* Partly holds. The size of the gap is a property of an extreme, stylised rule. Real streak-keeping behaviour is unlikely to be this pure. The direction is not a pure tautology, since it survives high coverage.
- *Change.* Sections 3.3, 6.2 and 7 now call A2 an extreme stylisation and say that its magnitude is not an estimate for any real behaviour. The EXP-003 report's sentence "costs retention through coverage" is qualified in its M4 note.

**C-3. The reported magnitude (-0.3068) is one point on a curve that depends on choices not grounded in data.**
- *Evidence.* K was chosen by a ceiling rule on A1, not from data. The exploratory K sweep gives -0.2358, -0.3164, -0.3078 and -0.2323 for K = 50, 100, 200 and 400, which is non-monotone. EXP-002 gives -0.1763 to -0.4709 across the grid.
- *Judgement.* Holds for any reading of -0.3068 as "the" effect size.
- *Change.* The abstract keeps the frozen primary value, since it is the registered estimand, and labels it "at the frozen default parameters". Section 6.3 adds the K dependence. Claims CLM-001 and CLM-005 carry the limit.

**C-4. If real forgetting is as flat as the held-out data suggest, the absolute gap could be small.**
- *Evidence.* Observed held-out recall falls only from 0.904 to 0.872 between 1 to 2 days and 32 to 90 days. The exponential form predicts 0.983 and 0.579. With slower forgetting the gap shrinks: -0.1226, -0.0661 and -0.0342 at h0 = 4, 8 and 16 times the fitted value (exploratory). At h0 of 540.72 and 1081.44 days, A2 is practically equivalent to no practice at all.
- *Counter-evidence.* In all three slow-forgetting rows A2 recovered about the same share of A1's gain over no practice (0.186 to 0.188, against 0.191 in EXP-001). The relative inefficiency of the rule is therefore stable, and only the stakes shrink. The flat Duolingo curve may also reflect which users and words reach long delays (selection in an adaptive product), not slow forgetting. This was not tested.
- *Judgement.* Holds as a limit on external relevance. The confirmatory verdicts are unaffected.
- *Change.* Section 6.3 and the limitations now state that the absolute gap scales with how much is forgotten, and that the real-data test does not support the time scale. The share-of-gain figure is reported as exploratory.

**C-5. The frozen design was chosen after the contrary sign had been seen.**
- *Evidence.* At the draft parameters (h0 = 1 day, K = 100), A2 - A1 was +0.0801 on smoke seeds. The amendments that moved the parameters off the floor were approved after those values were visible. At the frozen parameters the sign is negative.
- *Mitigation in the record.* The amendment method was committed (29d0dfb) before the fit. K was chosen by a rule on the control arms only. No A2 contrast was computed at the frozen parameters before the freeze. The values were disclosed in protocol section 14.7.
- *Judgement.* Partly holds. The mitigation is real, but researcher degrees of freedom in the decision to leave the floor regime cannot be excluded. Moreover, the floor-regime result is itself a "when" answer: under near-total forgetting, daily easy practice beat sparse round-robin.
- *Change.* The abstract now names the sign reversal. Section 5.5 is retitled as contradictory evidence and kept at full weight in the discussion of "when" (section 6.3).

**C-6. "Timing does not matter" overstates a small but systematic effect.**
- *Evidence.* A2 - F-EASY (daily versus 3 per week, under easiest-first) is -0.0110 to -0.0150 with every 95% interval excluding 0. The interaction is -0.0087 to -0.0183, and its exp-diff 95% interval reaches -0.0198, close to the SESOI.
- *Judgement.* Holds. Under the frozen rule these effects are "practically equivalent", but they are detectably negative and consistent in sign: daily timing makes easiest-first selection slightly worse.
- *Change.* Section 6.2 now says "small and below the SESOI, but detectably negative in combination with easiest-first selection", instead of "did not change retention".

**C-7. A3's equivalence to A1 is presented too generally.**
- *Evidence.* A3 was below A1 in all 9 cells at h0 = 33.8 days (EXP-002, relevant in 8) and at K = 400 (exploratory, -0.0621).
- *Judgement.* Holds.
- *Change.* Section 6.2 now limits the statement "same activity, same retention as A1" to the default parameters and longer half-lives, and names both exceptions. CLM-003 now carries this limit.

## B. Overgeneralisation and external claims

**C-8. Agreement with prior work is presented as support, but the model encodes that prior work.**
- *Evidence.* The difficulty-dependent gain and the retrieval-practice update were chosen from the spacing and testing literature. Agreement with it is therefore partly by construction.
- *Judgement.* Holds.
- *Change.* Section 6.4 now says that the direction is consistent with these sources because the model encodes their assumptions, and that the simulation is not independent evidence for them.

**C-9. Unsourced empirical statements about applications.**
- *Evidence.* The draft said that "learning applications often display activity streaks" (abstract) and that "many learning applications count activity" (section 1.1). No source for either was read.
- *Judgement.* Holds.
- *Change.* Both sentences were rewritten as definitions, with no prevalence claim.

**C-10. "Well documented" from a single abstract.**
- *Evidence.* Section 1.2 said that the benefits of testing are "well documented in the abstracts read". Only one testing abstract was read.
- *Judgement.* Holds.
- *Change.* The sentence now cites what that one abstract reports.

**C-11. Practical significance phrased as a design recommendation.**
- *Evidence.* Section 6.5 said that activity counts "should not be treated as a proxy for retention" in system design. A simulation can show that such a proxy can fail. It cannot show how often it fails in practice.
- *Judgement.* Holds.
- *Change.* The section now says that the model is an existence example: a policy can maximise activity metrics while losing retention, and an activity metric alone cannot tell such a policy from a good one (A2 and A3 have identical activity).

**C-12. "Order of magnitude longer streaks."**
- *Evidence.* The longest streak was 16.24 days against 1.88 days, a factor of about 8.6.
- *Judgement.* Holds as a precision issue.
- *Change.* Replaced by "about eight times longer".

## C. Statistics, leakage, stale material and missing runs

**C-13. Tiny intervals and "27 of 27" suggest more evidence than there is.**
- *Evidence.* d_z = -7.40 and intervals of width about 0.005 describe simulation noise. The 27 EXP-002 cells share learners, and EXP-003's exp-diff variant reproduces the EXP-002 default cell exactly (-0.3089) because both use seeds 1 to 5 with 100 learners. These are not independent replications.
- *Judgement.* Holds as framing.
- *Change.* The limitations section now says that cell counts are not independent confirmations and that the EXP-002 and EXP-003 default results coincide by design.

**C-14. Leakage of held-out data into the calibration or the design.**
- *Evidence checked.* h0 was fitted on the fit split only (J-0009). The held-out split was evaluated once, after the freeze (J-0014, revision c942be0), and nothing was refitted afterwards. Smoke seeds (9001 to 9005) and confirmatory seeds (1 to 5) never mixed. The M4 exploratory runs used smoke seeds only.
- *Judgement.* Does not hold. No leakage was found.

**C-15. Missing failed runs.**
- *Evidence checked.* 70,000 of 70,000 confirmatory learner-arms reported status ok (recomputed from the raw files in M4). The refused EXP-003 launch (J-0016) and the discarded early smoke attempts (J-0002, J-0003) are in the journal. The 14,000 M4 exploratory learner-arms had 0 failures.
- *Judgement.* Does not hold.

**C-16. Stale or mislabelled figures and records.**
- *Evidence.* Figure IDs repeat across experiments (FIG-01a exists in EXP-001, EXP-002 and EXP-003 with different content). The EXP-002 FIG-01a/01b show the first grid cell only. The experiment registry still said "report.md not written". The EXP-003 report states a wrong maximum timing contrast (0.0188, a selection contrast). The `frozen_analysis.json` files record an absolute local path.
- *Judgement.* Partly holds. No figure shows wrong data (checksums equal to the generated files), but labels and records were stale or wrong.
- *Change.* The manuscript uses experiment-qualified figure files (`EXP-00N_FIG-...`). The registry was updated. The EXP-003 error is corrected in an M4 note in that report. The absolute path is recorded in the audit; it is not fixed, since regenerating frozen-analysis files is not needed for any number.

**C-17. The held-out negative result is under-weighted.**
- *Evidence.* The draft mentions the result in the abstract and in section 5.4. A sceptic could argue that it invalidates the time scale of all three experiments.
- *Judgement.* Does not hold as stated. The held-out test was preregistered as descriptive and does not test H1. The draft already reports it at full weight, including in the abstract. Its consequence (C-4) is now discussed more fully.

## D. Challenges considered and rejected

- **The scheduler's belief is misspecified, so "easiest first" is not truly easiest.** Does not hold for the main result: A2's success rate of 0.987 shows that the belief ranking did find easy items. Misspecification in the non-default variants is by design and disclosed.
- **Residual minutes favour A1.** Does not hold: A2's mean residual was 2.15 slots, the exclusion sensitivity changes nothing at four decimals in EXP-001, and the gap is largest at q = 1.0, where there is no carry-forward.

## Changes made (manuscript 0.9 to 1.0)

| Section | Change | Challenge |
|---|---|---|
| Title | "Streaks without retention" replaced by a title naming item selection and activity counts | C-1 |
| Abstract | Unsourced prevalence sentence removed; the frozen value labelled as default-parameter; selection, not timing, as the finding; floor-regime sign reversal and the held-out negative result named | C-1, C-3, C-5, C-9 |
| 1.1, 1.2 | Prevalence claims removed; "well documented" replaced by the one abstract read | C-9, C-10 |
| 3.3 | A2 described as an extreme stylisation | C-2 |
| 5.5 | Retitled "Contradictory evidence: the floor regime" | C-5 |
| 6.1 | Activity counts cannot separate A2 from A3 | C-1, C-11 |
| 6.2 | Coverage as one channel, not the whole; timing small but detectably negative with easiest-first; A3 equivalence limited | C-2, C-6, C-7 |
| 6.3 | K dependence; slow-forgetting shrinkage; stable share of gain; floor regime as part of the "when" answer | C-3, C-4, C-5 |
| 6.4 | Agreement with prior work is by construction | C-8 |
| 6.5 | Existence example instead of a recommendation | C-11 |
| 5.1 | "About eight times longer" | C-12 |
| 7 | Non-independent cells; coinciding default results; pre-freeze degrees of freedom; time scale | C-4, C-5, C-13 |
| Figures | Experiment-qualified figure files | C-16 |
