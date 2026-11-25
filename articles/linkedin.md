<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
<!-- Draft for the owner. Not published. Numbers are identical to research/paper/manuscript.md (checked by tests/test_demo_consistency.py). -->

Can a learning streak keep growing while retention falls behind?

With a disclosed AI research assistant, I built a small, preregistered simulation of synthetic learners to ask when activity streaks diverge from retention. Every policy got the same practice time; only how that time was spread over days and items changed.

One defensible finding: in the model, a stylised streak-driven policy (practise every day, easiest items first) doubled active days, yet its mean expected recall 30 days later differed from a fixed three-sessions-a-week schedule's by -0.3068 (95% CI -0.3093 to -0.3042; 1,000 synthetic learners). A spaced-repetition rule with exactly the same streaks did not lose that retention. The cost came from which items were practised, not from practising daily.

Caveat: these are simulated learners, not people, and not any real app. A held-out test on real Duolingo data did not support the model's forgetting curve, and in a near-total-forgetting regime the sign reversed. Independent research, not peer reviewed; AI assistance disclosed.

Manuscript, reports and code: [repository URL: placeholder]
Interactive page: [demo URL: placeholder]
