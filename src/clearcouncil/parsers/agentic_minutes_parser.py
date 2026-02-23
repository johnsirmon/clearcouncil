"""
Agentic Minutes Parser — AI-powered extraction of voting records from inconsistently
formatted government meeting minutes.

The parser uses a multi-strategy approach:
1. Format detection: Identify the document structure (IQM2, Legistar, custom minutes, etc.)
2. Regex extraction: Apply known patterns for structured formats.
3. AI fallback: For unstructured or unknown formats, use an LLM with chain-of-thought
   reasoning to extract voting records.

The AI step leverages the GitHub AI inference API (free with GitHub token) or OpenAI
as an alternative. It uses a structured prompt that instructs the model to reason
step-by-step ("think aloud") before outputting structured JSON.

Supported document formats:
- IQM2 portal PDFs (York County SC, Spartanburg, etc.)
- Granicus/Legistar PDFs (Mecklenburg NC, Charleston SC, etc.)
- Standard commissioner/council meeting minutes (most NC/SC counties)
- Unstructured narrative minutes
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.models import VotingRecord
from ..core.exceptions import ClearCouncilError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document format detection
# ---------------------------------------------------------------------------

class DocumentFormat(str, Enum):
    IQM2 = "iqm2"
    LEGISTAR = "legistar"
    STANDARD_MINUTES = "standard_minutes"
    NARRATIVE = "narrative"
    UNKNOWN = "unknown"


FORMAT_SIGNATURES: Dict[DocumentFormat, List[str]] = {
    DocumentFormat.IQM2: [
        "iqm2.com",
        "MOVANT:",
        "SECOND:",
    ],
    DocumentFormat.LEGISTAR: [
        "legistar.com",
        "Motion By:",
        "Seconded By:",
        "Action Result",
    ],
    DocumentFormat.STANDARD_MINUTES: [
        "MOTION CARRIED",
        "MOTION FAILED",
        "moved by Commissioner",
        "Motion by Commissioner",
        "seconded by Commissioner",
        "vote was as follows",
        "the motion passed",
        "the motion failed",
        "moved to approve",
        "moved to adopt",
    ],
}


def detect_document_format(text: str) -> DocumentFormat:
    """
    Detect the document format based on signature strings.

    Returns the most likely DocumentFormat enum value.
    """
    text_lower = text.lower()
    scores: Dict[DocumentFormat, int] = {fmt: 0 for fmt in FORMAT_SIGNATURES}

    for fmt, signatures in FORMAT_SIGNATURES.items():
        for sig in signatures:
            if sig.lower() in text_lower:
                scores[fmt] += 1

    best_fmt = max(scores, key=lambda f: scores[f])
    if scores[best_fmt] == 0:
        return DocumentFormat.UNKNOWN
    return best_fmt


# ---------------------------------------------------------------------------
# Regex-based extraction for known formats
# ---------------------------------------------------------------------------

# IQM2 patterns (York County SC style)
_IQM2_RESULT_RE = re.compile(
    r"(APPROVED|DENIED|FAILED|PASSED|TABLED|WITHDRAWN|DEFERRED)",
    re.IGNORECASE,
)
_IQM2_MOVANT_RE = re.compile(r"MOVANT:\s*\n?\s*(.+?)(?:\n|$)", re.IGNORECASE)
_IQM2_SECOND_RE = re.compile(r"SECOND:\s*\n?\s*(.+?)(?:\n|$)", re.IGNORECASE)
_IQM2_AYES_RE = re.compile(r"AYES:\s*\n?\s*(.+?)(?:\n|$)", re.IGNORECASE)
_IQM2_NAYS_RE = re.compile(r"NAYS:\s*\n?\s*(.+?)(?:\n|$)", re.IGNORECASE)

# Standard minutes patterns (NC commissioner style)
_STD_MOTION_RE = re.compile(
    r"(?:"
    r"(?:moved|motion)\s+(?:by|was\s+made\s+by)\s+(?:Commissioner\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    r"|Commissioner\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:moved|made\s+a\s+motion)"
    r")",
    re.IGNORECASE,
)
_STD_SECOND_RE = re.compile(
    r"seconded\s+(?:by\s+)?(?:Commissioner\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
    re.IGNORECASE,
)
_STD_RESULT_RE = re.compile(
    r"(MOTION\s+(?:CARRIED|FAILED|PASSED|DENIED)|APPROVED|DENIED|PASSED|FAILED|UNANIMOUS)",
    re.IGNORECASE,
)
_STD_AYES_RE = re.compile(
    r"(?:Ayes|Aye|Yes|For):\s*([A-Za-z,\s]+?)(?=\n|Nays|Nay|No|Absent|$)",
    re.IGNORECASE,
)
_STD_NAYS_RE = re.compile(
    r"(?:Nays|Nay|No|Against):\s*([A-Za-z,\s]+?)(?=\n|Ayes|Aye|Yes|Absent|$)",
    re.IGNORECASE,
)

# Legistar patterns
_LEGISTAR_ACTION_RE = re.compile(
    r"Action:\s*(APPROVED|DENIED|FAILED|PASSED|TABLED|REFERRED|ACCEPTED|REJECTED)",
    re.IGNORECASE,
)
_LEGISTAR_MOTION_RE = re.compile(
    r"Motion\s+By:\s+(?:Commissioner\s+)?([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)*)",
    re.IGNORECASE,
)
_LEGISTAR_SECOND_RE = re.compile(
    r"Seconded\s+By:\s+(?:Commissioner\s+)?([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)*)",
    re.IGNORECASE,
)


def _extract_iqm2_records(text: str) -> List[VotingRecord]:
    """Extract voting records from IQM2-format documents."""
    records = []
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        result_match = _IQM2_RESULT_RE.search(line)

        if result_match:
            record = VotingRecord()
            record.result = result_match.group(1).upper()

            # Look ahead up to 20 lines for MOVANT/SECOND/AYES
            context = "\n".join(lines[i : i + 20])
            movant_m = _IQM2_MOVANT_RE.search(context)
            second_m = _IQM2_SECOND_RE.search(context)
            ayes_m = _IQM2_AYES_RE.search(context)
            nays_m = _IQM2_NAYS_RE.search(context)

            if movant_m:
                record.movant = movant_m.group(1).strip()
                record.representative = record.movant
            if second_m:
                record.second = second_m.group(1).strip()
            if ayes_m:
                record.ayes = ayes_m.group(1).strip()
            if nays_m:
                record.nays = nays_m.group(1).strip()

            if record.movant or record.ayes:
                records.append(record)

        i += 1

    return records


def _extract_standard_minutes_records(text: str) -> List[VotingRecord]:
    """Extract voting records from standard commissioner meeting minutes."""
    records = []
    # Split on paragraph-like blocks (single or double newlines)
    paragraphs = re.split(r"\n{2,}", text) if "\n\n" in text else [text]

    for para in paragraphs:
        motion_m = _STD_MOTION_RE.search(para)
        result_m = _STD_RESULT_RE.search(para)

        if motion_m and result_m:
            record = VotingRecord()
            # Pick whichever capture group matched
            movant = (motion_m.group(1) or motion_m.group(2) or "").strip()
            record.movant = movant
            record.representative = record.movant
            record.result = result_m.group(1).strip().upper()

            second_m = _STD_SECOND_RE.search(para)
            if second_m:
                record.second = second_m.group(1).strip()

            ayes_m = _STD_AYES_RE.search(para)
            if ayes_m:
                record.ayes = ayes_m.group(1).strip()

            nays_m = _STD_NAYS_RE.search(para)
            if nays_m:
                record.nays = nays_m.group(1).strip()

            records.append(record)

    return records


def _extract_legistar_records(text: str) -> List[VotingRecord]:
    """Extract voting records from Legistar-format documents."""
    records = []
    sections = re.split(r"(?=Action:\s*)", text, flags=re.IGNORECASE)

    for section in sections:
        action_m = _LEGISTAR_ACTION_RE.search(section)
        motion_m = _LEGISTAR_MOTION_RE.search(section)

        if action_m:
            record = VotingRecord()
            record.result = action_m.group(1).upper()

            if motion_m:
                record.movant = motion_m.group(1).strip()
                record.representative = record.movant

            second_m = _LEGISTAR_SECOND_RE.search(section)
            if second_m:
                record.second = second_m.group(1).strip()

            ayes_m = _STD_AYES_RE.search(section)
            if ayes_m:
                record.ayes = ayes_m.group(1).strip()

            records.append(record)

    return records


# ---------------------------------------------------------------------------
# AI-powered extraction
# ---------------------------------------------------------------------------

_AGENTIC_SYSTEM_PROMPT = """You are an expert at extracting voting records from local government meeting minutes.
Your task is to identify every vote that occurred in the provided text and return them as structured JSON.

Think step-by-step:
1. Read through the text and identify all voting events (motions, resolutions, ordinances that were voted on)
2. For each vote, extract:
   - movant: who made the motion (first and last name)
   - second: who seconded the motion (first and last name)
   - result: APPROVED, DENIED, PASSED, FAILED, TABLED, WITHDRAWN, or UNANIMOUS
   - ayes: names of members voting yes (comma-separated)
   - nays: names of members voting no (comma-separated)
   - abstain: names of members abstaining (comma-separated, if any)
   - absent: names of absent members (comma-separated, if any)
   - subject: brief description of what was voted on

3. Return ONLY valid JSON in this exact format:
{
  "reasoning": "Brief explanation of what formats and patterns you detected",
  "votes": [
    {
      "movant": "First Last",
      "second": "First Last",
      "result": "APPROVED",
      "ayes": "Name1, Name2",
      "nays": "Name3",
      "abstain": "",
      "absent": "",
      "subject": "Brief description"
    }
  ]
}

If a field is unknown or not mentioned, use an empty string "".
Do not include any text outside the JSON object."""

_AGENTIC_USER_PROMPT_TEMPLATE = """Extract all voting records from these meeting minutes:

---
{text}
---

Return only the JSON response."""


def _call_github_ai(text: str) -> Optional[str]:
    """
    Call the GitHub AI inference API for agentic extraction.

    Uses the github/copilot-4o model (or falls back to gpt-4o-mini).
    Requires GITHUB_TOKEN environment variable.
    """
    import urllib.request
    import urllib.error

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.debug("GITHUB_TOKEN not set; skipping AI extraction")
        return None

    api_base = os.getenv("GITHUB_API_BASE_URL", "https://models.inference.ai.azure.com")
    url = f"{api_base}/chat/completions"

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": _AGENTIC_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _AGENTIC_USER_PROMPT_TEMPLATE.format(
                    text=text[:6000]  # Limit to avoid token overflow
                ),
            },
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "ClearCouncil/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        logger.warning(f"GitHub AI API call failed: {e}")
        return None


def _call_openai(text: str) -> Optional[str]:
    """
    Call the OpenAI API for agentic extraction.

    Requires OPENAI_API_KEY environment variable.
    """
    import urllib.request
    import urllib.error

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": _AGENTIC_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _AGENTIC_USER_PROMPT_TEMPLATE.format(text=text[:6000]),
            },
        ],
        "temperature": 0.1,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "ClearCouncil/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        logger.warning(f"OpenAI API call failed: {e}")
        return None


def _parse_ai_response(response_text: str) -> List[VotingRecord]:
    """Parse the JSON response from the AI model into VotingRecord objects."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed text
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if not json_match:
            logger.warning("Could not parse AI response as JSON")
            return []
        try:
            data = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return []

    if "reasoning" in data:
        logger.debug(f"AI reasoning: {data['reasoning']}")

    records = []
    for vote in data.get("votes", []):
        record = VotingRecord()
        record.movant = vote.get("movant", "").strip()
        record.representative = record.movant
        record.second = vote.get("second", "").strip()
        record.result = vote.get("result", "").strip().upper()
        record.ayes = vote.get("ayes", "").strip()
        record.nays = vote.get("nays", "").strip()
        # Store additional fields in metadata if VotingRecord supports it
        subject = vote.get("subject", "").strip()
        if subject and hasattr(record, "subject"):
            record.subject = subject
        records.append(record)

    return records


def _extract_agentic(text: str) -> List[VotingRecord]:
    """
    Use AI with chain-of-thought reasoning to extract voting records.

    Tries GitHub AI first (free), then falls back to OpenAI.
    Returns empty list if neither is available.
    """
    # Try GitHub AI first (free with GitHub token)
    response = _call_github_ai(text)
    if response:
        records = _parse_ai_response(response)
        if records:
            logger.info(f"AI extracted {len(records)} voting records")
            return records

    # Fall back to OpenAI
    response = _call_openai(text)
    if response:
        records = _parse_ai_response(response)
        if records:
            logger.info(f"OpenAI extracted {len(records)} voting records")
            return records

    logger.warning("AI extraction unavailable; no records extracted for unknown format")
    return []


# ---------------------------------------------------------------------------
# Main parser class
# ---------------------------------------------------------------------------

@dataclass
class ExtractionResult:
    """Result of an agentic extraction attempt."""

    records: List[VotingRecord]
    document_format: DocumentFormat
    method_used: str       # "regex", "ai", or "hybrid"
    ai_reasoning: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class AgenticMinutesParser:
    """
    AI-powered parser for government meeting minutes with inconsistent formatting.

    Strategy:
    1. Detect document format from text signatures.
    2. Apply the appropriate regex-based extractor.
    3. If regex finds zero records OR format is UNKNOWN, fall back to AI extraction.
    4. Combine and deduplicate results.
    """

    def __init__(self, use_ai: bool = True, ai_threshold: int = 0):
        """
        Args:
            use_ai: Whether to use AI extraction when regex fails.
            ai_threshold: If regex finds <= this many records, also attempt AI extraction.
        """
        self.use_ai = use_ai
        self.ai_threshold = ai_threshold

    def parse(self, text: str) -> ExtractionResult:
        """
        Parse meeting minutes text and extract voting records.

        Args:
            text: Raw text content of the meeting minutes.

        Returns:
            ExtractionResult with records and metadata about the extraction.
        """
        doc_format = detect_document_format(text)
        logger.info(f"Detected document format: {doc_format.value}")

        regex_records: List[VotingRecord] = []
        method = "regex"

        if doc_format == DocumentFormat.IQM2:
            regex_records = _extract_iqm2_records(text)
        elif doc_format == DocumentFormat.LEGISTAR:
            regex_records = _extract_legistar_records(text)
        elif doc_format == DocumentFormat.STANDARD_MINUTES:
            regex_records = _extract_standard_minutes_records(text)
        else:
            logger.info("Unknown document format; will attempt AI extraction")

        # Use AI if format is unknown or regex found few results
        if self.use_ai and (
            doc_format == DocumentFormat.UNKNOWN
            or len(regex_records) <= self.ai_threshold
        ):
            logger.info("Attempting AI-powered extraction...")
            ai_records = _extract_agentic(text)

            if ai_records:
                if regex_records:
                    # Merge: prefer AI records but keep any regex-only ones
                    combined = ai_records + [
                        r for r in regex_records if not _is_duplicate(r, ai_records)
                    ]
                    return ExtractionResult(
                        records=combined,
                        document_format=doc_format,
                        method_used="hybrid",
                    )
                return ExtractionResult(
                    records=ai_records,
                    document_format=doc_format,
                    method_used="ai",
                )

        warnings = []
        if not regex_records:
            warnings.append(
                f"No voting records found in {doc_format.value} format. "
                "Consider enabling AI extraction (use_ai=True) or checking the document."
            )

        return ExtractionResult(
            records=regex_records,
            document_format=doc_format,
            method_used=method,
            warnings=warnings,
        )

    def parse_file(self, path: Path) -> ExtractionResult:
        """Parse a PDF or text file."""
        path = Path(path)
        if path.suffix.lower() == ".pdf":
            text = self._extract_pdf_text(path)
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
        return self.parse(text)

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        """Extract text from a PDF file using PyPDF2 or pdfminer."""
        try:
            import PyPDF2
            text_parts = []
            with open(path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)
                for page in reader.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except ImportError:
            pass

        try:
            from pdfminer.high_level import extract_text
            return extract_text(str(path))
        except ImportError:
            raise ClearCouncilError(
                "PDF text extraction requires PyPDF2 or pdfminer.six. "
                "Install with: pip install PyPDF2"
            )


def _is_duplicate(record: VotingRecord, existing: List[VotingRecord]) -> bool:
    """Check if a record is a duplicate of any in the existing list."""
    for ex in existing:
        if (
            ex.movant
            and record.movant
            and ex.movant.lower() == record.movant.lower()
            and ex.result
            and record.result
            and ex.result.upper() == record.result.upper()
        ):
            return True
    return False
