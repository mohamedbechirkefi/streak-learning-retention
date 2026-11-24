<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# experiments/

Exploratory smoke configurations (seeds 9001 to 9005 only, label `exploratory`). Confirmatory draft configurations live in `research/experiments/EXP-NNN/config.json` and are refused by the runner until the owner freezes the protocols.

| Config | ID | Purpose |
|---|---|---|
| `smoke-exp001.json` | SMOKE-EXP-001 | Smoke matrix of protocol section 10: 4 arms x 5 smoke seeds x 20 learners (default of `streak.cli smoke`) |
| `smoke-exp001-n200.json` | SMOKE-EXP-001-N200 | Full-size EXP-001 matrix on smoke seeds: runtime and seed spread |
| `smoke-exp002.json` | SMOKE-EXP-002 | 27-cell EXP-002 grid, 20 learners per seed: degenerate cells and runtime |
| `smoke-exp003.json` | SMOKE-EXP-003 | 6 policy cells x 4 model variants, 20 learners per seed: degenerate cells and runtime |
