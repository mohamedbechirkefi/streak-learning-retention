<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# results/exploratory/

**Exploratory only.** Smoke runs on development seeds 9001 to 9005, made before the protocol freeze to measure runtime, seed spread and degenerate cases (M2 brief). They are not findings, are never pooled with confirmatory results and must not be cited as results of EXP-001 to EXP-003. Journal entries: J-0004 to J-0007 (J-0002 and J-0003 record earlier, discarded attempts) in `research/experiment_journal.jsonl`.

Each folder holds `run_manifest.json` and `report/` (`report.md`, `analysis.json`, `metrics.csv`, `contrasts.csv`, `figures/*.svg`). `SMOKE-EXP-001/` also holds its raw `results.json` and `report/report.pdf`.

Regenerate (raw files of the larger runs go to the git-ignored `results/raw/exploratory/`):

    uv run python -m streak.cli smoke --pdf
    uv run python -m streak.cli run --config experiments/smoke-exp001-n200.json --out results/raw/exploratory/SMOKE-EXP-001-N200
    uv run python -m streak.cli report --results results/raw/exploratory/SMOKE-EXP-001-N200/results.json --out results/exploratory/SMOKE-EXP-001-N200/report
    (same pair of commands for smoke-exp002.json / SMOKE-EXP-002 and smoke-exp003.json / SMOKE-EXP-003)

Result files are byte-identical on rerun with the same code and platform (tested); manifests differ in timestamps, runtime and memory.
