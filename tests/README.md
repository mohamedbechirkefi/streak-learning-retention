<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# tests/

Run with `uv run pytest` or `uv run python -m streak.cli test`. The pass and fail counts of each run are recorded in `progress.md`, never assumed.

| File | Covers |
|---|---|
| `test_memory.py` | Forgetting-curve bounds, monotonicity, p = 0.5 at the half-life, hand-computed values, update rules, invalid inputs (property tests with Hypothesis) |
| `test_params.py` | Parameter defaults against protocol section 10, invalid parameters, arm definitions |
| `test_scheduling.py` | Planned slots, item selection and ties, fixed-day and make-up rule, daily arms on every available day, one review per item per day, replay of A2's belief, integer-parameter regression (D-008) |
| `test_budget.py` | Time-budget conservation (spent + residual = M), daily cap, no practice on unavailable days (property tests) |
| `test_controls_golden.py` | No-practice control against the closed form, hand-computed golden learners, make-up and cap golden example, invalid inputs |
| `test_differential.py` | Engine against an independent naive pure-Python reference, all arms, both forms and gain rules |
| `test_population.py` | Determinism and common random numbers across cells |
| `test_stats.py` | Bootstrap, Holm, classification, Spearman |
| `test_schema.py` | Committed configs valid; malformed configs and results rejected; confirmatory configs match the protocol matrices |
| `test_runner.py` | Integration config to results, byte-identical reruns, recorded failures, cell expansion, G-FREEZE refusal, git_dirty |
| `test_report_cli.py` | Report numbers recomputed from records, SVG validity, malformed results rejected, CLI commands |
