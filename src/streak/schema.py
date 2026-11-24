# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Versioned JSON schemas and a minimal validator (no third-party dependency).

The schema files in ``streak/schemas/`` are the single source of truth. The
validator implements the JSON Schema keywords those files use: type, required,
properties, additionalProperties (false only), items, enum, const, minimum,
maximum, minItems, maxItems and pattern.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).parent / "schemas"
SCHEMAS = {
    "streak.config/1.0": "config-1.0.schema.json",
    "streak.result/1.0": "result-1.0.schema.json",
    "streak.manifest/1.0": "manifest-1.0.schema.json",
}


class SchemaError(ValueError):
    """Raised when a document does not conform to its schema (fail closed)."""


@lru_cache(maxsize=None)
def load_schema(schema_id: str) -> dict:
    if schema_id not in SCHEMAS:
        raise SchemaError(f"unknown schema id {schema_id!r}; known: {sorted(SCHEMAS)}")
    return json.loads((SCHEMA_DIR / SCHEMAS[schema_id]).read_text())


_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v == v
    and v not in (float("inf"), float("-inf")),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _errors(doc: Any, sch: dict, path: str, out: list[str]) -> None:
    if "const" in sch and doc != sch["const"]:
        out.append(f"{path}: expected {sch['const']!r}, got {doc!r}")
        return
    if "enum" in sch and doc not in sch["enum"]:
        out.append(f"{path}: {doc!r} not in {sch['enum']}")
        return
    if "type" in sch:
        types = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        if not any(_TYPES[t](doc) for t in types):
            out.append(f"{path}: expected type {types}, got {type(doc).__name__}")
            return
    if isinstance(doc, (int, float)) and not isinstance(doc, bool):
        if "minimum" in sch and doc < sch["minimum"]:
            out.append(f"{path}: {doc} < minimum {sch['minimum']}")
        if "maximum" in sch and doc > sch["maximum"]:
            out.append(f"{path}: {doc} > maximum {sch['maximum']}")
    if isinstance(doc, str) and "pattern" in sch and not re.search(sch["pattern"], doc):
        out.append(f"{path}: {doc!r} does not match {sch['pattern']}")
    if isinstance(doc, list):
        if "minItems" in sch and len(doc) < sch["minItems"]:
            out.append(f"{path}: fewer than {sch['minItems']} items")
        if "maxItems" in sch and len(doc) > sch["maxItems"]:
            out.append(f"{path}: more than {sch['maxItems']} items")
        if "items" in sch:
            for i, item in enumerate(doc):
                _errors(item, sch["items"], f"{path}[{i}]", out)
    if isinstance(doc, dict):
        for key in sch.get("required", []):
            if key not in doc:
                out.append(f"{path}: missing required key {key!r}")
        props = sch.get("properties", {})
        if sch.get("additionalProperties") is False:
            for key in doc:
                if key not in props:
                    out.append(f"{path}: unexpected key {key!r}")
        for key, sub in props.items():
            if key in doc:
                _errors(doc[key], sub, f"{path}.{key}", out)


def validation_errors(doc: Any, schema_id: str, limit: int = 20) -> list[str]:
    out: list[str] = []
    _errors(doc, load_schema(schema_id), "$", out)
    return out[:limit]


def validate(doc: Any, schema_id: str) -> None:
    """Raise SchemaError listing (up to 20) violations; return None if valid."""
    errs = validation_errors(doc, schema_id)
    if errs:
        raise SchemaError(f"document does not conform to {schema_id}:\n  " + "\n  ".join(errs))
