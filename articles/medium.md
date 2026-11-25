<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
<!-- Draft for the owner. Not published. Numbers are identical to research/paper/manuscript.md (checked by tests/test_demo_consistency.py). -->

# Busy every day, remembering less: what a learner simulation says about activity streaks

*Mohamed Bechir Kefi. Draft, not published. Independent research, not peer reviewed. An AI system (Claude, Anthropic) was used as a disclosed research and development assistant.*

A streak counts the days in a row on which you practised. It is easy to measure and easy to reward. What learning is for, though, is retention: being able to recall something days or weeks later. Those are different quantities. This project asked a narrow question about the gap between them: **when can activity streaks diverge from knowledge retention in a learning model?**

Everything below comes from a simulation of synthetic learners. It describes a model, not people, and not any real app.

## The set-up

Each synthetic learner studies 200 items once and then has the same practice time, 336 minutes over 56 days, under one of four policies:

- **A0 NoPractice**: nothing after the first study (a control).
- **A1 Fixed**: three fixed sessions a week, going through the items in order.
- **A2 Streak**: practise every available day and, in each short session, review the items the scheduler believes are easiest. This is a deliberately extreme stylisation of "keep the streak alive with quick wins".
- **A3 Spaced**: the same daily timing as A2, but a threshold rule that reviews items whose estimated recall has dropped to 0.9 or below first.

Memory follows a forgetting curve; a successful review lengthens an item's half-life, more so when the item was harder to recall. The median initial half-life, 67.59 days, was fitted to public Duolingo traces. The protocol, including the primary metric and the decision rule, was written and frozen before any confirmatory run. The primary metric, R30, is the mean expected recall over all items 30 days after practice ends.

## What happened

The streak-driven policy was busier and remembered less. A2 practised on 47.55 days on average against 23.60 for the fixed schedule, and its longest streak was 16.24 days against 1.88. Its R30 was 0.4863 against 0.7931. The paired difference was **-0.3068 (95% CI -0.3093 to -0.3042)** over 1,000 synthetic learners.

The most telling comparison is A2 against A3. They have exactly the same active days, streaks and minutes. Yet A3 retained 0.3182 more. An activity metric cannot tell these two policies apart.

## Why: which items, not which days

A third experiment separated timing (every day or three times a week) from selection (easiest first, in order, or threshold-based). Easiest-first selection lowered R30 by 0.20 to 0.39 at either timing. Practising every day by itself did not change retention by more than the smallest effect size of interest, 0.02. Under a flat gain rule, a test that could have invalidated this reading, the gap was larger, not smaller.

Across a 27-cell grid of forgetting speeds, gains and availability, the gap appeared in every cell, from -0.4709 to -0.1763.

## What did not fit

Two results cut the other way, and they matter as much as the main one.

- **The real data did not support the forgetting curve.** On held-out Duolingo first repeats, the model's exponential curve fitted worse than simply predicting a constant recall rate (log-likelihood per trial -0.3865 against -0.3352). Observed recall fell only from 0.904 to 0.872 across delays of 1 to 90 days. The simulated time scale is therefore not validated.
- **The sign can reverse.** At early draft parameters where nearly everything was forgotten by the test, daily easy practice beat sparse round-robin (+0.0801, exploratory, seen before the freeze). The divergence needs a regime in which neglected items have something to lose.

## What this does and does not show

It is an existence example: a scheduling policy can maximise activity measures while losing most of the retention that the same minutes could buy. It does not show how often this happens with real learners or products. Practice time was held fixed, so it says nothing about whether streaks help people practise more.

## Explore and reproduce

The interactive page shows every result with its interval, including the negative ones, and lets you run the model in your browser. It collects nothing and has no streaks or reminders of its own.

- Repository and manuscript: [repository URL: placeholder, not yet published]
- Interactive page: [demo URL: placeholder, not yet published]
- Experiment reports: `research/experiments/EXP-001/report.md`, `EXP-002/report.md`, `EXP-003/report.md`

*Figure suggestion: the "Streak versus recall" chart from the interactive page. Alt text: "Mean R30 against mean active days for four policies; A2 Streak and A3 Spaced share the same activity, 47.55 days, but A2 Streak's recall is far lower."*
