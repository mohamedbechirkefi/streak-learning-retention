<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# src/

Python package `streak` (M2, engine 1.1.0 since the round-2 amendments). All outputs are simulations of synthetic learners.

| Module | Role |
|---|---|
| `params.py` | Validated model parameters (units in docstrings) and arm definitions A0 to A3, plus the EXP-003 cells D-RR, F-EASY, F-DUE |
| `memory.py` | Forgetting curves (exponential, power-law) and half-life update rules (difficulty-dependent, flat) |
| `population.py` | Synthetic learner generation from `SeedSequence` children (common random numbers) |
| `simulate.py` | One learner under one arm: planned slots, carry-forward, daily cap, item selection, scheduler belief |
| `metrics.py` | Per learner-arm metrics of protocol section 5 |
| `stats.py` | Stratified percentile bootstrap, SESOI classification, Holm, Spearman, paired summaries |
| `runner.py` | Config to validated result file and run manifest; G-FREEZE gate for confirmatory configs |
| `schema.py`, `schemas/` | Versioned JSON schemas (config, result, manifest) and a dependency-free validator |
| `manifest.py` | Git revision, versions, OS, CPU, peak memory |
| `report.py` | Tables (CSV, Markdown), SVG figures, report, optional PDF (pandoc to Typst) |
| `cli.py` | `smoke`, `run`, `report`, `test` |

Decisions: D-006 (layout), D-007 (implementation readings of the draft protocol), D-008 (float coercion fix).
