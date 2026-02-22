"""Utilities for retrieving and normalizing article text from URLs."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen


class _ArticleTextParser(HTMLParser):
    """Best-effort HTML to text parser for article extraction."""

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._skip_depth > 0:
            return
        text = data.strip()
        if text:
            self._parts.append(text)

    def to_text(self) -> str:
        # Collapse whitespace and filter very short fragments to reduce navigation noise.
        normalized = [re.sub(r"\s+", " ", part).strip() for part in self._parts]
        filtered = [part for part in normalized if len(part) >= 20]
        return "\n".join(filtered)


def fetch_article_text(source_url: str, timeout_seconds: int = 12) -> str:
    """Fetch URL content and return extracted readable text."""
    request = Request(
        source_url,
        headers={"User-Agent": "ClearCouncilNext/0.1 (+https://github.com/johnsirmon/clearcouncil)"},
    )

    with urlopen(request, timeout=timeout_seconds) as response:  # nosec B310
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            raise ValueError("URL did not return HTML content")

        encoding = response.headers.get_content_charset() or "utf-8"
        raw_html = response.read().decode(encoding, errors="replace")

    parser = _ArticleTextParser()
    parser.feed(raw_html)
    text = parser.to_text()

    if len(text) < 80:
        raise ValueError("Fetched content is too short for reliable auditing")

    return text
