"""Source auditing for factual grounding, bias signals, and objective translation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class BiasSignal:
    """A single explainable bias indicator."""

    category: str
    phrase: str
    sentence: str
    severity: str


@dataclass
class SourceAuditResult:
    """Structured audit output for a source article."""

    factual_claims: List[str]
    bias_signals: List[BiasSignal]
    bias_score: int
    factual_density: float
    bias_summary: str
    objective_translation: str
    investigation_prompts: List[str]


# These are intentionally conservative to avoid over-flagging normal reporting language.
BIAS_LEXICON = {
    "loaded_language": [
        "outrageous",
        "shocking",
        "disgraceful",
        "radical",
        "corrupt",
        "rigged",
        "disaster",
        "cover-up",
    ],
    "certainty_without_evidence": [
        "obviously",
        "clearly",
        "undeniably",
        "everyone knows",
        "no doubt",
    ],
    "speculative": [
        "might",
        "could",
        "possibly",
        "allegedly",
        "rumored",
    ],
    "anonymous_authority": [
        "sources say",
        "insiders say",
        "people familiar",
        "according to sources",
    ],
}

FACT_HINT_PATTERN = re.compile(
    r"(\b\d{1,4}\b|\$\s?\d|percent|%|on\s+\w+\s+\d{1,2}|approved|voted|awarded|adopted)",
    flags=re.IGNORECASE,
)


def _sentence_split(text: str) -> List[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [p.strip() for p in parts if len(p.strip()) > 20]


def _iter_bias_signals(sentences: Iterable[str]) -> List[BiasSignal]:
    signals: List[BiasSignal] = []
    for sentence in sentences:
        lowered = sentence.lower()
        for category, phrases in BIAS_LEXICON.items():
            for phrase in phrases:
                if phrase in lowered:
                    severity = "high" if category in {"loaded_language", "anonymous_authority"} else "medium"
                    signals.append(
                        BiasSignal(
                            category=category,
                            phrase=phrase,
                            sentence=sentence[:280],
                            severity=severity,
                        )
                    )
    return signals


def _extract_factual_claims(sentences: Iterable[str], max_claims: int = 10) -> List[str]:
    claims: List[str] = []
    for sentence in sentences:
        lowered = sentence.lower()
        has_bias_term = any(term in lowered for terms in BIAS_LEXICON.values() for term in terms)
        if has_bias_term:
            continue

        if FACT_HINT_PATTERN.search(sentence):
            claims.append(sentence)
        if len(claims) >= max_claims:
            break

    return claims


def _build_objective_translation(factual_claims: List[str]) -> str:
    if not factual_claims:
        return (
            "This article contains limited verifiable detail. Review original sources, "
            "official records, and quoted documents before drawing conclusions."
        )

    selected = factual_claims[:4]
    joined = " ".join(selected)
    return (
        "Objective summary: The article reports the following verifiable points. "
        f"{joined} "
        "Statements that use emotionally charged wording or unnamed sources should be treated as claims requiring corroboration."
    )


def _build_investigation_prompts(factual_claims: List[str], bias_signals: List[BiasSignal]) -> List[str]:
    prompts = [
        "Which official document, vote record, contract, or filing confirms each key claim?",
        "Are there primary-source links for numbers, dates, and quoted statements?",
    ]

    if any(s.category == "anonymous_authority" for s in bias_signals):
        prompts.append("Which claims rely on unnamed sources, and can those claims be independently verified?")

    if factual_claims:
        prompts.append("Do the reported figures match public records for the same time period and agency?")

    return prompts


def audit_source_text(article_text: str) -> SourceAuditResult:
    """Audit text for factual density, bias cues, and objective translation."""
    sentences = _sentence_split(article_text)

    bias_signals = _iter_bias_signals(sentences)
    factual_claims = _extract_factual_claims(sentences)

    factual_density = round((len(factual_claims) / max(len(sentences), 1)) * 100, 1)
    bias_score = min(100, len(bias_signals) * 8)

    if bias_score >= 55:
        bias_summary = "High rhetorical risk: interpret with caution and seek primary sources."
    elif bias_score >= 25:
        bias_summary = "Moderate rhetorical risk: mixed factual reporting and persuasive framing."
    else:
        bias_summary = "Low rhetorical risk: mostly descriptive language with fewer bias cues."

    return SourceAuditResult(
        factual_claims=factual_claims,
        bias_signals=bias_signals,
        bias_score=bias_score,
        factual_density=factual_density,
        bias_summary=bias_summary,
        objective_translation=_build_objective_translation(factual_claims),
        investigation_prompts=_build_investigation_prompts(factual_claims, bias_signals),
    )
