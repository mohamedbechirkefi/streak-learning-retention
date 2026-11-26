<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# demo/: STREAK interactive research page (M5)

A static page built from the shared lab template (TypeScript, React and Vite, pinned versions, `package-lock.json`). It shows:

- an overview with the status label and three measured key figures;
- **streak versus recall** (EXP-001): active days and longest streak against R30 with 95% intervals;
- **memory curves**: the model's recall 1 to 90 days after practice (EXP-001) and the held-out real-data test, in which the forgetting curve did not fit;
- every experiment and test with its estimates, intervals and verdict, including the negative and contradictory results, and the EXP-002 cell chart and EXP-003 effects chart;
- a **playground** (sandbox) with scenario, seed and learner-count controls, Run, Cancel and Reset, showing a **learning timeline**, memory curves and a streak versus recall table for the run;
- assumptions, method and limitations.

Labels distinguish measured results (confirmatory simulation), real-data results, exploratory results, sandbox output and assumption values.

## Data

`public/data/results.json` is written by `scripts/export_demo_data.py` from committed results only (schema `lab-demo-results` 1.0.0 plus STREAK-specific keys). Every display string occurs verbatim in the manuscript or, as a documented exception, in an experiment report; `tests/test_demo_consistency.py` checks this and that a fresh export equals the committed file. The loader fails closed: if validation fails, no number is shown.

## Sandbox

`src/engine.ts` is a port of the Python engine (engine 1.1.0). Fed the Python engine's own random draws (`src/fixtures/engine_fixture.json`, written by `scripts/export_sandbox_fixture.py` on smoke seed 9001), it reproduces the review trace exactly and every real-valued output within 1e-9 (`src/engine.test.ts`). In the browser it draws its own random numbers, so sandbox seeds are not research seeds and sandbox numbers are not research results; a second test checks its population means against the Python engine within about 4 standard errors. Runs are bounded (at most 200 learners and 400 items) and cancellable.

## Commands

    npm ci && npm test && npm run build && npm run preview
    node tools/a11y_check.mjs dist --screenshots <dir>

The page runs offline after the first load, makes no request to any other host, uses no external font, analytics or storage, and collects nothing from visitors. It has no streaks, rewards, reminders or prompts to return. Demo URL: https://streak-learning-retention.kefimohamedbechir.workers.dev.

## Hosting

The built page (`dist/`) is hosted as Cloudflare Workers static assets on the free plan, configured by `wrangler.jsonc` (assets only, no Worker script). It is deployed by the coordinator, not by any script of this repository.
