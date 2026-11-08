from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
import hashlib
import json
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


@dataclass
class Source:
    source_id: str
    title: str
    url: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    citation_count: int | None = None
    query: str | None = None
    retrieved_at: str = field(default_factory=utc_now)
    source_type: Literal["paper", "web", "dataset", "code"] = "paper"


@dataclass
class Evidence:
    evidence_id: str
    source_id: str
    excerpt: str
    locator: str | None = None
    evidence_type: Literal["primary", "secondary", "method", "result", "limitation"] = "secondary"
    supports: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reviewed_by: str | None = None


@dataclass
class Claim:
    claim_id: str
    statement: str
    status: Literal["supported", "contradicted", "unverified"] = "unverified"
    source_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    notes: str = ""


@dataclass
class Hypothesis:
    hypothesis_id: str
    statement: str
    rationale: str
    predictions: list[str] = field(default_factory=list)
    parent_id: str | None = None
    status: Literal["proposed", "testing", "supported", "rejected", "inconclusive"] = "proposed"
    score: float | None = None


@dataclass
class ExperimentRecord:
    experiment_id: str
    hypothesis_id: str
    command: list[str]
    status: Literal["queued", "running", "completed", "failed", "timed_out"] = "queued"
    metrics: dict[str, float] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    artifacts: list[str] = field(default_factory=list)
    seed: int | None = None
    started_at: str | None = None
    finished_at: str | None = None


@dataclass
class ResearchState:
    run_id: str
    topic: str
    question: str
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    stage: str = "planning"
    iteration: int = 0
    agents: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    experiments: list[ExperimentRecord] = field(default_factory=list)
    search_tree: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    paper_draft: str = ""
    validation_errors: list[str] = field(default_factory=list)
    tasks: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def new(cls, topic: str, question: str) -> "ResearchState":
        return cls(
            run_id=f"edgex_{uuid.uuid4().hex[:12]}",
            topic=topic,
            question=question,
            agents=[
                "EdgeX-Orchestrator",
                "EdgeX-Scout",
                "EdgeX-Architect",
                "EdgeX-Builder",
                "EdgeX-Executor",
                "EdgeX-Referee",
                "EdgeX-Scribe",
                "EdgeX-Statistician",
                "EdgeX-Mathematician",
                "EdgeX-Domain-Scientist",
                "EdgeX-Context-Manager",
                "EdgeX-Reproducibility",
            ],
        )

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ResearchState":
        def build(item: dict[str, Any], typ: Any) -> Any:
            return typ(**item)

        payload = dict(payload)
        payload["sources"] = [build(x, Source) for x in payload.get("sources", [])]
        payload["evidence"] = [build(x, Evidence) for x in payload.get("evidence", [])]
        payload["claims"] = [build(x, Claim) for x in payload.get("claims", [])]
        payload["hypotheses"] = [build(x, Hypothesis) for x in payload.get("hypotheses", [])]
        payload["experiments"] = [build(x, ExperimentRecord) for x in payload.get("experiments", [])]
        return cls(**payload)

    def json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)
