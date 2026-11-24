# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Raw Duolingo traces -> processed first-repeat observations (protocol section 14.2).

Reads data/raw/settles.acl16.learning_traces.13m.csv.gz, applies the pure function
streak.duolingo.ingest, writes data/processed/first_repeat.npz (no identifiers) and
data/processed/ingest_summary.json (counts). Both are git-ignored.

Usage: .venv/bin/python scripts/ingest_duolingo.py
"""

import json
import sys
from pathlib import Path

from streak import duolingo as dl
from streak.manifest import sha256_file

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "settles.acl16.learning_traces.13m.csv.gz"
OUT = ROOT / "data" / "processed"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    proc = dl.ingest(dl.read_rows(RAW))
    dl.save_processed(proc, OUT / "first_repeat.npz")
    summary = {"raw_file": str(RAW.relative_to(ROOT)), "raw_sha256": sha256_file(RAW),
               "processed_file": "data/processed/first_repeat.npz",
               "processed_sha256": sha256_file(OUT / "first_repeat.npz"), **proc.counts()}
    (OUT / "ingest_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
