<!-- SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0 -->
# EXP-001 reproduction

Run from the repository root on a clean checkout of the recorded revision (see `run_manifest.json`).

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest
.venv/bin/python scripts/run_confirmatory.py EXP-001          # guard: clean tree, frozen hashes, raw data hash
.venv/bin/python scripts/analyse_confirmatory.py EXP-001      # tables, figures, frozen analysis -> generated/
cp research/experiments/EXP-001/generated/figures/*.svg research/experiments/EXP-001/figures/
cp research/experiments/EXP-001/generated/metrics.csv research/experiments/EXP-001/metrics.csv
cp results/confirmatory/EXP-001/run_manifest.json research/experiments/EXP-001/run_manifest.json
```

- Raw result file: `results/confirmatory/EXP-001/results.json` (schema `streak.result/1.0`); SHA-256 in `results/confirmatory/EXP-001/sha256_manifest.json`.
- Provenance per run (id, config hash, seed, revision, data manifest hash, hardware, start and end, exit status): `results/confirmatory/EXP-001/provenance.json`.
- Expected: byte-identical `results.json` on the same platform with the same seeds and config (protocol section 8); across platforms, metrics equal to floating-point tolerance (1e-12 relative was not tested across platforms: unverified).
- The raw Duolingo file is needed only for the run guard's data hash check; rebuild it with `scripts/download_duolingo.py` (SHA-256 in `data/manifest.json`).
