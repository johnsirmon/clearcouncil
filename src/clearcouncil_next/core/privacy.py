"""PII and secret redaction helpers."""

from __future__ import annotations

import re
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(ghp_[A-Za-z0-9]{20,})"),
    re.compile(r"(github_pat_[A-Za-z0-9_]{20,})"),
    re.compile(r"(sk-[A-Za-z0-9]{20,})"),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)([^\s]+)"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)([^\s,;]+)"),
    re.compile(r"(?i)(token\s*[=:]\s*)([^\s,;]+)"),
]

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact_sensitive_text(value: str) -> str:
    """Redact common secret/token/email patterns from a string."""
    result = value
    for pattern in SECRET_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    result = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", result)
    return result


def redact_object(value: Any) -> Any:
    """Recursively redact sensitive data in simple objects."""
    if isinstance(value, str):
        return redact_sensitive_text(value)
    if isinstance(value, dict):
        return {k: redact_object(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_object(v) for v in value]
    return value
