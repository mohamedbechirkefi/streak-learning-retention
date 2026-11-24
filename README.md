<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# STREAK: Are we learning or just maintaining streaks? (working title)

**Question.** When can activity streaks diverge from knowledge retention in a learning model?

**Status: M2 (core implementation) done for the draft protocol.** No confirmatory experiment has been run and there are no findings. Only exploratory smoke runs on development seeds exist (`results/exploratory/`); they are not results. The research protocol is a draft awaiting the owner's freeze. All future results will come from simulations of synthetic learners and will hold only within the model's assumptions; they will not be claims about real human learning or about any commercial product.

## Why it matters

Learning applications often display activity streaks. Activity and retention are different things: a learner can be active every day while practising mostly what they already know. This project asks, in a controlled simulation with matched practice minutes, whether and when streak-driven practice can raise activity measures without raising retention.

## What is implemented

The simulation engine (`src/streak`): synthetic learners with forgetting, retrieval practice and a fixed practice budget; scheduling arms A0 (no practice), A1 (fixed three sessions a week), A2 (streak-driven, easiest first), A3 (most due first) and the EXP-003 timing-by-selection cells; versioned result schemas, run manifests, a report generator and a CLI. Tests: see `tests/README.md` and `progress.md` for actual counts. Not implemented yet: confirmatory runs (await the owner's freeze), experiment reports, manuscript, demo. See `roadmap.md`.

## Research navigation

| Item | Location |
|---|---|
| Draft protocol | [research/protocol.md](research/protocol.md) |
| Feasibility audit | [research/feasibility.md](research/feasibility.md) |
| Experiment registry | [research/experiment_registry.csv](research/experiment_registry.csv) |
| Manuscript (skeleton) | [research/paper/manuscript.md](research/paper/manuscript.md) |
| Claims register (empty) | [research/claims_register.csv](research/claims_register.csv) |
| Pre-freeze amendment proposals | [research/protocol_amendment_proposals.md](research/protocol_amendment_proposals.md) |
| Exploratory smoke outputs (not results) | [results/exploratory/](results/exploratory/README.md) |
| Roadmap and progress | [roadmap.md](roadmap.md), [progress.md](progress.md) |

| Experiment | Question | Status |
|---|---|---|
| EXP-001 | Streak-driven versus fixed practice at matched minutes | planned; exploratory smoke run only (protocol draft, awaiting owner freeze) |
| EXP-002 | Robustness across forgetting parameters and availability | planned; exploratory smoke run only (protocol draft, awaiting owner freeze) |
| EXP-003 | Timing versus item selection; model-form sensitivity | planned; exploratory smoke run only (protocol draft, awaiting owner freeze) |

## Quick start

```
uv sync --frozen
uv run python -m streak.cli test     # test suite
uv run python -m streak.cli smoke    # exploratory smoke run on seeds 9001-9005, with report
```

`uv run python -m streak.cli run --config research/experiments/EXP-001/config.json` is refused until the owner freezes the protocol.

## Data

Synthetic data only. External datasets were audited for licences but not downloaded; see [data/manifest.json](data/manifest.json).

## Licence

STREAK Source-Available Non-Commercial Research License v1.0 (`LicenseRef-STREAK-NC-Research-1.0`), a custom licence that is not OSI approved. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). Third-party material keeps its own terms.

## Citation

See [CITATION.cff](CITATION.cff). AI assistance is disclosed: the AI acts as a research and development assistant; the owner holds authority over hypotheses, protocol freezes, claims and publication.
