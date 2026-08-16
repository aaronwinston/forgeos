from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field

PUBLISHABLE_THRESHOLD = 4
REGRESSION_DROP_THRESHOLD = -1

WORKFLOW_DIMENSIONS: dict[str, list[str]] = {
    "blog": ["editorial_quality", "technical_accuracy", "developer_fluency", "brand_fit"],
    "launch": ["editorial_quality", "technical_accuracy", "brand_fit", "claims_risk"],
    "analyst": ["editorial_quality", "technical_accuracy", "brand_fit", "claims_risk"],
}

DIMENSION_RUBRIC_FILES: dict[str, str] = {
    "editorial_quality": "rubrics/editorial-quality.md",
    "technical_accuracy": "rubrics/technical-accuracy.md",
    "developer_fluency": "rubrics/developer-fluency.md",
    "brand_fit": "rubrics/brand-fit.md",
    "claims_risk": "core/CLAIMS_POLICY.md",
}

HYPE_TERMS = {
    "unlock",
    "unleash",
    "revolutionary",
    "game-changing",
    "seamless",
    "next-generation",
    "leverage",
    "utilize",
    "cutting-edge",
    "transformative",
    "powerful",
    "robust",
    "excited to announce",
    "thrilled to share",
    "delighted",
}

TECHNICAL_TERMS = {
    "eval",
    "evaluation",
    "trace",
    "span",
    "observability",
    "latency",
    "retrieval",
    "prompt",
    "tool",
    "api",
    "regression",
    "benchmark",
    "workflow",
    "failure mode",
}

RISKY_CLAIM_TERMS = {
    "best",
    "leader",
    "leading",
    "number one",
    "first",
    "guaranteed",
    "proven",
    "always",
    "never fails",
}


class DimensionScore(BaseModel):
    dimension: str
    rubric_file: str
    score: int
    passed: bool
    reason: str


class RegressionDelta(BaseModel):
    dimension: str
    current_score: int
    baseline_score: int
    delta: int


class EvalResult(BaseModel):
    workflow_type: str
    overall_score: float
    gate_passed: bool
    failed_dimensions: list[str] = Field(default_factory=list)
    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    regression_checked: bool = False
    regression_failed: bool = False
    regression_deltas: list[RegressionDelta] = Field(default_factory=list)


@dataclass(frozen=True)
class BaselineSnapshot:
    run_id: int
    dimension_scores: list[DimensionScore]


def _clamp(score: int) -> int:
    return max(1, min(5, score))


def _count_phrase_hits(text: str, phrases: set[str]) -> int:
    total = 0
    for phrase in phrases:
        total += len(re.findall(rf"\\b{re.escape(phrase)}\\b", text))
    return total


def _score_editorial_quality(text: str) -> tuple[int, str]:
    score = 3
    reasons: list[str] = []

    word_count = len(text.split())
    if word_count >= 120:
        score += 1
        reasons.append("sufficient depth")

    structure_hits = sum(
        marker in text
        for marker in ["\n## ", "\n### ", "1.", "2.", "step", "checklist"]
    )
    if structure_hits >= 2:
        score += 1
        reasons.append("clear structure")

    if "in today" in text or "rapidly evolving landscape" in text:
        score -= 1
        reasons.append("generic framing")

    if text.count("\n\n") < 1:
        score -= 1
        reasons.append("limited paragraph structure")

    final = _clamp(score)
    return final, ", ".join(reasons) if reasons else "baseline structure and clarity"


def _score_technical_accuracy(text: str) -> tuple[int, str]:
    score = 3
    reasons: list[str] = []

    technical_hits = _count_phrase_hits(text, TECHNICAL_TERMS)
    if technical_hits >= 4:
        score += 1
        reasons.append("uses precise technical terms")
    if "tradeoff" in text or "limitation" in text:
        score += 1
        reasons.append("acknowledges limitations")

    if re.search(r"\b\d+%\s+(faster|better|improvement|reduction|lift)\b", text):
        score -= 1
        reasons.append("unsourced quantitative claim")

    if "observability replaces evaluation" in text:
        score -= 1
        reasons.append("category term misuse")

    final = _clamp(score)
    return final, ", ".join(reasons) if reasons else "acceptable technical precision"


def _score_developer_fluency(text: str) -> tuple[int, str]:
    score = 3
    reasons: list[str] = []

    technical_hits = _count_phrase_hits(text, TECHNICAL_TERMS)
    if technical_hits >= 5:
        score += 1
        reasons.append("developer-specific vocabulary")

    if "```" in text or "api" in text or "failure mode" in text:
        score += 1
        reasons.append("concrete workflow detail")

    hype_hits = _count_phrase_hits(text, HYPE_TERMS)
    if hype_hits > 0:
        score -= 1
        reasons.append("contains hype phrasing")

    if "magic" in text:
        score -= 1
        reasons.append("treats AI as magic")

    final = _clamp(score)
    return final, ", ".join(reasons) if reasons else "developer framing is present"


def _score_brand_fit(text: str) -> tuple[int, str]:
    score = 3
    reasons: list[str] = []

    hype_hits = _count_phrase_hits(text, HYPE_TERMS)
    if hype_hits == 0:
        score += 1
        reasons.append("avoids banned hype language")
    else:
        score -= 1
        reasons.append("contains banned hype language")

    if re.search(r"\b(trace|rubric|regression|evidence|workflow)\b", text):
        score += 1
        reasons.append("evidence-led framing")

    if len(text.split()) < 80:
        score -= 1
        reasons.append("too short for substantive brand voice")

    final = _clamp(score)
    return final, ", ".join(reasons) if reasons else "voice is broadly aligned"


def _score_claims_risk(text: str) -> tuple[int, str]:
    score = 5
    reasons: list[str] = []

    risky_hits = _count_phrase_hits(text, RISKY_CLAIM_TERMS)
    if risky_hits:
        score -= min(3, risky_hits)
        reasons.append("contains risky/superlative claim language")

    if re.search(r"\b\d+%\s+(faster|better|improvement|reduction|lift)\b", text):
        score -= 2
        reasons.append("unsourced performance claim")

    if "http://" in text or "https://" in text or "source:" in text:
        score += 1
        reasons.append("includes citation marker")

    final = _clamp(score)
    return final, ", ".join(reasons) if reasons else "no obvious claims-risk patterns"


SCORERS = {
    "editorial_quality": _score_editorial_quality,
    "technical_accuracy": _score_technical_accuracy,
    "developer_fluency": _score_developer_fluency,
    "brand_fit": _score_brand_fit,
    "claims_risk": _score_claims_risk,
}


def _normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").lower()
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _build_dimension_scores(workflow_type: str, artifact_text: str) -> list[DimensionScore]:
    if workflow_type not in WORKFLOW_DIMENSIONS:
        raise ValueError(f"Unsupported workflow_type: {workflow_type}")

    normalized = _normalize_text(artifact_text)
    scores: list[DimensionScore] = []

    for dimension in WORKFLOW_DIMENSIONS[workflow_type]:
        raw_score, reason = SCORERS[dimension](normalized)
        scores.append(
            DimensionScore(
                dimension=dimension,
                rubric_file=DIMENSION_RUBRIC_FILES[dimension],
                score=raw_score,
                passed=raw_score >= PUBLISHABLE_THRESHOLD,
                reason=reason,
            )
        )

    return scores


def _compute_regression(
    current_scores: list[DimensionScore],
    baseline_scores: list[DimensionScore],
) -> tuple[bool, list[RegressionDelta]]:
    baseline_map = {item.dimension: item.score for item in baseline_scores}
    deltas: list[RegressionDelta] = []

    for current in current_scores:
        if current.dimension not in baseline_map:
            continue
        baseline_score = baseline_map[current.dimension]
        delta = current.score - baseline_score
        deltas.append(
            RegressionDelta(
                dimension=current.dimension,
                current_score=current.score,
                baseline_score=baseline_score,
                delta=delta,
            )
        )

    regression_failed = any(delta.delta <= REGRESSION_DROP_THRESHOLD for delta in deltas)
    return regression_failed, deltas


def evaluate_workflow_artifact(
    workflow_type: str,
    artifact_text: str,
    baseline: Optional[BaselineSnapshot] = None,
) -> EvalResult:
    dimension_scores = _build_dimension_scores(workflow_type, artifact_text)
    overall_score = round(
        sum(item.score for item in dimension_scores) / max(1, len(dimension_scores)),
        2,
    )
    failed_dimensions = [item.dimension for item in dimension_scores if not item.passed]

    regression_failed = False
    regression_deltas: list[RegressionDelta] = []
    if baseline:
        regression_failed, regression_deltas = _compute_regression(
            current_scores=dimension_scores,
            baseline_scores=baseline.dimension_scores,
        )

    gate_passed = len(failed_dimensions) == 0 and not regression_failed

    return EvalResult(
        workflow_type=workflow_type,
        overall_score=overall_score,
        gate_passed=gate_passed,
        failed_dimensions=failed_dimensions,
        dimension_scores=dimension_scores,
        regression_checked=baseline is not None,
        regression_failed=regression_failed,
        regression_deltas=regression_deltas,
    )


def serialize_dimension_scores(scores: list[DimensionScore]) -> str:
    payload = [
        {
            "dimension": item.dimension,
            "rubric_file": item.rubric_file,
            "score": item.score,
            "passed": item.passed,
            "reason": item.reason,
        }
        for item in scores
    ]
    payload.sort(key=lambda row: row["dimension"])
    return json.dumps(payload, sort_keys=True)


def parse_dimension_scores(raw: str) -> list[DimensionScore]:
    parsed = json.loads(raw or "[]")
    if not isinstance(parsed, list):
        return []
    return [DimensionScore(**item) for item in parsed]


def serialize_regression_deltas(deltas: list[RegressionDelta]) -> str:
    payload = [
        {
            "dimension": item.dimension,
            "current_score": item.current_score,
            "baseline_score": item.baseline_score,
            "delta": item.delta,
        }
        for item in deltas
    ]
    payload.sort(key=lambda row: row["dimension"])
    return json.dumps(payload, sort_keys=True)


def parse_regression_deltas(raw: str) -> list[RegressionDelta]:
    parsed = json.loads(raw or "[]")
    if not isinstance(parsed, list):
        return []
    return [RegressionDelta(**item) for item in parsed]
