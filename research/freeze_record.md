<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# Freeze record: STREAK protocol 1.0 (owner-approved 2026-11-24)

Machine-readable twin: `research/freeze.json` (read by the run guard in `src/streak/runner.py`).

## Owner approval

- First round, 2026-11-24 (`_shared/owner-approvals-2026-11-24.md`): the owner answered "yes for all others" to the M2 decision list, which covered the STREAK amendment proposals.
- Second round, 2026-11-24 (`_shared/owner-approvals-2026-11-24b.md`): the owner answered "Approve all". For STREAK: adopt "the same Duolingo logs" only if "a licence recheck is clean", fallback "stay synthetic"; amendments "Move the parameters off the recall floor (fitted from Duolingo if the licence is clean). Replace the strawman arm A3 with a meaningful comparator under a stated rule. Fix the Holm wording. Disclose that A2 > A1 was seen."

## Common decisions

- **C1 Data.** Real data as approved, synthetic otherwise. The Duolingo traces (Settles and Meeder 2016, doi:10.7910/DVN/N8XJME) passed the licence recheck (CC BY-NC 4.0, read 2026-11-24, D-011) and are adopted to calibrate h0 (fit user split) and for a preregistered second test (held-out user split). Every simulated learner is synthetic.
- **C2 PDFs.** pandoc and Typst (`-V mainfont="Libertinus Serif"`); no LaTeX on the machine.
- **C3 Authorship.** Mohamed Bechir Kefi, no affiliation. The AI is disclosed as a research and development assistant, not an author (CITATION.cff, manuscript metadata).
- **C4 Disclosure.** Exploratory values of the primary contrast A2 minus A1 (R30) were seen before the freeze, all on smoke seeds 9001 to 9005 at the draft parameters (h0 = 1 day, K = 100, old A3), engine 1.0.1, commit dfa9dd4:
  - SMOKE-EXP-001-N200 (n = 1,000): +0.0801, 95% interval 0.0788 to 0.0813 (`results/exploratory/SMOKE-EXP-001-N200/report/contrasts.csv`, J-0005).
  - SMOKE-EXP-001 (n = 100): +0.0768 (`results/exploratory/SMOKE-EXP-001/report/contrasts.csv`, J-0004).
  - SMOKE-EXP-002: mean difference above 0 in 23 of 27 cells, range -0.0787 to +0.0920 (`results/exploratory/SMOKE-EXP-002/report/contrasts.csv`, J-0006).
  - SMOKE-EXP-003: +0.0768 (exponential, difficulty gain), +0.0848 (exponential, flat), +0.0245 (power, difficulty), +0.0855 (power, flat) (`results/exploratory/SMOKE-EXP-003/report/contrasts.csv`, J-0007).
  - After the amendments, only the control arms A0 and A1 were simulated (floor check, J-0010: A0 0.410, A1 0.791 at K = 200). No A2 or A3 run and no contrast was computed at the frozen parameters. The held-out Duolingo split was not evaluated.

## What was amended before the freeze (protocol section 14)

| Item | Applied | Detail |
|---|---|---|
| Real data (R2-1) | yes | Duolingo traces; h0 fitted on the fit split = 67.59 days (J-0009); held-out second test preregistered (P§14.4) |
| Off the recall floor | yes | h0 = 67.59 days; K = 200 by the control-only floor check (J-0010); EXP-002 h0 axis {33.8, 67.59, 135.18} |
| A3 comparator (R2-2) | yes | threshold-based spaced repetition, r* = 0.9 (P§14.5), also F-DUE in EXP-003 |
| Holm wording (R2-3) | yes | P§14.6; EXP-002 adds Holm across cells for the primary contrast |
| Disclosure A2 > A1 (R2-4) | yes | P§14.7 and C4 above |
| AP-3, AP-4, AP-6 | no | not in the owner's approved list for STREAK |

The method was committed (29d0dfb) before the fit; the fitted values were committed in 02eb104.

## Hashes (SHA-256)

| File | SHA-256 |
|---|---|
| `research/protocol.md` (1.0) | 57a60597a93cfc07a1d25e9a2f6bac9f23009b554d3d9820828e7707210711ee |
| `research/experiments/EXP-001/protocol.md` | d618b9f8dbc09079702ad4bb9dd19c0595753b8f2985638e3cbe1fbec4585f32 |
| `research/experiments/EXP-002/protocol.md` | 16f54294c4d6db58acf6a7957ebedfed47e7226c5fe997ba42f1841675131c7e |
| `research/experiments/EXP-003/protocol.md` | 20fc86cd0d595776589525cfd76153abae7c1c88b5faefbbdcc7b9f0c798cfba |
| `research/experiments/EXP-001/config.json` (file) | f58c9114ee1d75aa829913a685e2dbb28b660220e85367ca4b6e423a74856798 |
| `research/experiments/EXP-002/config.json` (file) | 8cfdabadfc5302420d718a7deb29aba7160543b89449cf23de32f1e61e037bf4 |
| `research/experiments/EXP-003/config.json` (file) | 6d7ac466084124cf55a566dfa789e91088033ed2f98eae49404a667ea6e9d589 |
| `data/manifest.json` | 60b024953faa4e164c83520fefd5b5a8d6e1154d8c18ed8067769ce4aed2ed9e |
| raw Duolingo file (not committed) | 26cf9b33f2e9b2e8aa9a8f262a017b30699ca2f625c56a12ce699d4ea7076873 |

Canonical config hashes (what the guard compares) are in `research/freeze.json`. Git revision of the frozen content: 02eb1046f542c65e01eae9449d66a4fdaca90135.

## Run guard

`streak.cli run` accepts a confirmatory config only if the registry hash matches the EXP protocol on disk, `research/protocol.md` is no longer marked as not frozen, and `research/freeze.json` matches the parent protocol, the data manifest and the config's canonical hash. Tests: `tests/test_runner.py` (frozen configs accepted at the gate without being run; 18 changed-config cases refused before any simulation; protocol or manifest edits refused on a copy) and `tests/test_report_cli.py` (CLI exit 3 on a changed config).

## Ratifications after the freeze

| Date | Item | Owner approval | Effect on hashes |
|---|---|---|---|
| 2026-11-24 (round 3) | K = 200 items, so that baseline A1 stays below the 0.8 ceiling (P§14.8, J-0010, D-013) | "Approve all" (`_shared/owner-approvals-2026-11-24c.md`, section 4); recorded as D-015 | none: the frozen files already contain K = 200 |
