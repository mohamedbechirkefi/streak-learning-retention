<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# STREAK: Are we learning or just maintaining streaks? (working title)

**Question.** When can activity streaks diverge from knowledge retention in a learning model?

**Status: M0 (bootstrap and feasibility).** No experiment has been run and there are no findings. The research protocol is a draft awaiting the owner's freeze. All future results will come from simulations of synthetic learners and will hold only within the model's assumptions; they will not be claims about real human learning or about any commercial product.

## Why it matters

Learning applications often display activity streaks. Activity and retention are different things: a learner can be active every day while practising mostly what they already know. This project asks, in a controlled simulation with matched practice minutes, whether and when streak-driven practice can raise activity measures without raising retention.

## What is implemented

Nothing yet beyond the control files, the feasibility audit, the source audit and the draft protocol (M0). See `roadmap.md` for the plan.

## Research navigation

| Item | Location |
|---|---|
| Draft protocol | [research/protocol.md](research/protocol.md) |
| Feasibility audit | [research/feasibility.md](research/feasibility.md) |
| Experiment registry | [research/experiment_registry.csv](research/experiment_registry.csv) |
| Manuscript (skeleton) | [research/paper/manuscript.md](research/paper/manuscript.md) |
| Claims register (empty) | [research/claims_register.csv](research/claims_register.csv) |
| Roadmap and progress | [roadmap.md](roadmap.md), [progress.md](progress.md) |

| Experiment | Question | Status |
|---|---|---|
| EXP-001 | Streak-driven versus fixed practice at matched minutes | planned (protocol draft, awaiting owner freeze) |
| EXP-002 | Robustness across forgetting parameters and availability | planned (protocol draft, awaiting owner freeze) |
| EXP-003 | Timing versus item selection; model-form sensitivity | planned (protocol draft, awaiting owner freeze) |

## Quick start

Not available yet (M2). Planned: `uv sync --frozen`, then `uv run python -m streak.cli smoke`.

## Data

Synthetic data only. External datasets were audited for licences but not downloaded; see [data/manifest.json](data/manifest.json).

## Licence

STREAK Source-Available Non-Commercial Research License v1.0 (`LicenseRef-STREAK-NC-Research-1.0`), a custom licence that is not OSI approved. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md). Third-party material keeps its own terms.

## Citation

See [CITATION.cff](CITATION.cff). AI assistance is disclosed: the AI acts as a research and development assistant; the owner holds authority over hypotheses, protocol freezes, claims and publication.
