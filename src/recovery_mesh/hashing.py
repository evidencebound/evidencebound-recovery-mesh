from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize JSON-compatible data deterministically for digest binding."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(value: Any) -> str:
    """Return a lowercase SHA-256 hex digest for structured or scalar data."""
    payload = value if isinstance(value, bytes) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
