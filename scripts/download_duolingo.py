# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Download the Duolingo half-life regression learning traces (Settles and Meeder 2016).

Source: Harvard Dataverse, doi:10.7910/DVN/N8XJME, file id 3091087
(settles.acl16.learning_traces.13m.csv.gz, 379,004,009 bytes, MD5
0a1cae5eb7ad4b0bd9c0de91d74fcced as published by Dataverse).
Licence (Dataverse terms of use, read 2026-11-24): CC BY-NC 4.0.

The file is written to data/raw/ (git-ignored: larger than 20 MB and holds
pseudonymous user ids at row level; never committed). A download record with
URL, size, MD5, SHA-256 and access time is written next to it. If the file is
already present with the published MD5, it is not downloaded again; the record
is refreshed with the hashes recomputed from disk.

Usage (from the repository root):
    .venv/bin/python scripts/download_duolingo.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
FILENAME = "settles.acl16.learning_traces.13m.csv.gz"
URL = "https://dataverse.harvard.edu/api/access/datafile/3091087"
DATASET_PAGE = "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/N8XJME"
EXPECTED_MD5 = "0a1cae5eb7ad4b0bd9c0de91d74fcced"
EXPECTED_SIZE = 379_004_009
MAX_BYTES = 2_000_000_000  # brief: stop above about 2 GB


def hashes(path: Path) -> tuple[str, str, int]:
    md5, sha = hashlib.md5(), hashlib.sha256()
    n = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            md5.update(chunk)
            sha.update(chunk)
            n += len(chunk)
    return md5.hexdigest(), sha.hexdigest(), n


def download(dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(URL, headers={"User-Agent": "streak-research-download/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as out:
        length = resp.headers.get("Content-Length")
        if length is not None and int(length) > MAX_BYTES:
            raise SystemExit(f"refusing: Content-Length {length} exceeds {MAX_BYTES} bytes")
        n = 0
        for chunk in iter(lambda: resp.read(1 << 20), b""):
            n += len(chunk)
            if n > MAX_BYTES:
                raise SystemExit(f"refusing: more than {MAX_BYTES} bytes received")
            out.write(chunk)
    tmp.replace(dest)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / FILENAME
    downloaded = False
    if not (dest.exists() and hashes(dest)[0] == EXPECTED_MD5):
        download(dest)
        downloaded = True
    md5, sha, size = hashes(dest)
    if md5 != EXPECTED_MD5 or size != EXPECTED_SIZE:
        print(f"error: MD5 {md5} / size {size} do not match the published {EXPECTED_MD5} / {EXPECTED_SIZE}",
              file=sys.stderr)
        return 1
    record = {
        "file": f"data/raw/{FILENAME}",
        "url": URL,
        "dataset_page": DATASET_PAGE,
        "doi": "10.7910/DVN/N8XJME",
        "license": "CC BY-NC 4.0 (Dataverse terms of use)",
        "size_bytes": size,
        "md5": md5,
        "sha256": sha,
        "downloaded_this_call": downloaded,
        "checked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (RAW / "download_record.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
