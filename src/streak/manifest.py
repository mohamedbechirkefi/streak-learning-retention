# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Run-environment capture for run manifests: git revision, versions, OS, CPU, memory."""

from __future__ import annotations

import hashlib
import json
import platform
import resource
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from . import ENGINE_VERSION, __version__


def repo_root() -> Path:
    """Repository root: the nearest ancestor of this file holding pyproject.toml, else cwd."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() and (parent / "research").is_dir():
            return parent
    return Path.cwd()


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_info(root: Path) -> tuple[str | None, bool | None]:
    try:
        rev = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True).stdout.strip()
        # Tracked files only: untracked run outputs must not mark the source revision dirty.
        dirty = bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                                    capture_output=True, text=True, check=True).stdout.strip())
        return rev, dirty
    except (OSError, subprocess.CalledProcessError):
        return None, None


def cpu_name() -> str:
    if sys.platform == "darwin":
        try:
            return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                  text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor() or platform.machine()


def peak_memory_bytes() -> int | None:
    """Peak resident set size of this process so far (ru_maxrss: bytes on macOS, KiB on Linux)."""
    try:
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(rss if sys.platform == "darwin" else rss * 1024)


def environment() -> dict[str, Any]:
    import os

    return {
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "streak": __version__, "engine": ENGINE_VERSION},
        "platform": {"os": platform.system(), "os_release": platform.release(),
                     "machine": platform.machine(), "cpu": cpu_name(), "cpu_count": os.cpu_count()},
    }
