from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json
import re
import time

from .execution import ExperimentExecutor
from .models import Claim, Evidence, ExperimentRecord, Hypothesis, ResearchState, Source, stable_id, utc_now
from .providers import DeterministicModel, ModelError, TextModel
from .retrieval import RetrievalError, merge_sources, search_both
from .store import RunStore
from .tree_search import ResearchTree
from .coordination import context_packet


AGENT_SYSTEM = """You are part of EdgeX, an evidence-gated scientific research team.
Never invent citations, data, experimental results, or equations. Separate established
evidence from hypotheses. Every factual claim must be traceable to a source or an
experiment record. If evidence is missing, write UNVERIFIED explicitly."""


class EvidenceGate:
    """Conservative validator: unsupported claims never become 'supported'."""

    def validate(self, state: ResearchState) -> list[str]:
        source_ids = {s.source_id for s in state.sources}
        evidence_ids = {e.evidence_id for e in state.evidence}
        errors: list[str] = []
        if not state.claims:
            errors.append("No claims have been assessed; research readiness cannot pass")
        for claim in state.claims:
            missing_sources = set(claim.source_ids) - source_ids
            missing_evidence = set(claim.evidence_ids) - evidence_ids
            if missing_sources or missing_evidence:
                claim.status = "unverified"
                errors.append(f"{claim.claim_id}: references missing provenance")
            elif not claim.source_ids and not claim.evidence_ids:
                claim.status = "unverified"
                errors.append(f"{claim.claim_id}: no provenance")
            elif claim.status == "supported":
                linked = [e for e in state.evidence if e.evidence_id in claim.evidence_ids]
                reviewed = [e for e in linked if e.source_id in source_ids and e.excerpt.strip()
                            and e.locator and e.locator.strip() and e.reviewed_by
                            and e.reviewed_by.strip() and claim.claim_id in e.supports]
                if not reviewed:
                    claim.status = "unverified"
                    errors.append(f"{claim.claim_id}: missing reviewed excerpt with a locator and support link")
            if claim.status != "supported" and not any(e.startswith(claim.claim_id + ":") for e in errors):
                errors.append(f"{claim.claim_id}: {claim.status}")
        state.validation_errors = errors
        return errors


class PaperWriter:
    def __init__(self, model: TextModel):
        self.model = model

    def write(self, state: ResearchState) -> str:
        EvidenceGate().validate(state)
        ledger = self._ledger(state)
        try:
            generated = self.model.complete(
                AGENT_SYSTEM + "\nWrite a clearly labeled draft manuscript using only the supplied ledger.",
                f"Topic: {state.topic}\nQuestion: {state.question}\nEvidence ledger:\n{ledger}",
            )
            if generated.strip() and not generated.startswith("No model call"):
                return "> Disclosure: Machine-generated EdgeX research draft. Claims require independent verification.\n\n" + generated.strip()
        except ModelError as exc:
            state.notes.append(f"Manuscript model failed; deterministic draft used: {exc}")
        return self._deterministic_draft(state)

    def _ledger(self, state: ResearchState) -> str:
        candidates = {
            "working_context": json.loads(context_packet(state, 12000)),
            "sources": [s.__dict__ for s in state.sources[:10]],
            "evidence": [e.__dict__ for e in state.evidence[:10]],
            "hypotheses": [h.__dict__ for h in state.hypotheses[:10]],
            "experiments": [{"experiment_id": e.experiment_id, "status": e.status, "metrics": e.metrics}
                            for e in state.experiments[-10:]],
        }
        packet = {"working_context": candidates.pop("working_context"),
                  "omitted_records": 0, "canonical_ledger": "state.json"}
        for key, items in candidates.items():
            packet[key] = []
            for item in items:
                packet[key].append(item)
                if len(json.dumps(packet)) > 47000:
                    packet[key].pop()
                    packet["omitted_records"] += 1
        return json.dumps(packet)

    def _deterministic_draft(self, state: ResearchState) -> str:
        supported = [c for c in state.claims if c.status == "supported"]
        unresolved = [c for c in state.claims if c.status != "supported"]
        source_lines = "\n".join(f"- [{s.source_id}] {s.title} ({s.year or 'n.d.'}) — {s.url}" for s in state.sources)
        claim_lines = "\n".join(f"- {c.statement} [{c.status}; {', '.join(c.source_ids or c.evidence_ids) or 'no provenance'}]" for c in state.claims)
        return f"""> Disclosure: Machine-generated EdgeX research draft. Claims require independent verification.
# {state.topic}

## Abstract

This is an evidence-gated research draft. It contains {len(supported)} supported claim(s)
and {len(unresolved)} claim(s) that remain unverified or contradicted. It is not a validated
scientific conclusion.

## Research question

{state.question}

## Current claims ledger

{claim_lines or '- No claims have been validated yet.'}

## Hypotheses

{chr(10).join(f'- {h.statement} — status: {h.status}' for h in state.hypotheses) or '- No hypotheses recorded.'}

## Experiments

{chr(10).join(f'- {e.experiment_id}: {e.status}; metrics={e.metrics}' for e in state.experiments) or '- No experiments recorded.'}

## Limitations and verification requirements

- This draft does not establish novelty, causality, or reproducibility.
- Every unsupported claim must be checked against the primary source or a completed experiment.
- Statistical uncertainty, leakage, baseline choice, compute budget, and negative results must be reported before submission.

## References

{source_lines or '- No sources retrieved.'}
"""


class EdgeXOrchestrator:
    """Long-running staged orchestrator combining AIDE-style search and AI-Scientist stages."""

    def __init__(self, run_dir: str | Path, model: TextModel | None = None, timeout_seconds: int = 3600):
        self.store = RunStore(run_dir)
        self.model = model or DeterministicModel()
        self.executor = ExperimentExecutor(timeout_seconds)
        self.gate = EvidenceGate()
        self.writer = PaperWriter(self.model)

    @classmethod
    def create(cls, topic: str, question: str, run_dir: str | Path) -> "EdgeXOrchestrator":
        orchestrator = cls(run_dir)
        if orchestrator.store.snapshot_path.exists():
            raise FileExistsError(f"Run already exists: {run_dir}")
        state = ResearchState.new(topic, question)
        orchestrator.store.save(state, "run_created", {"agents": state.agents})
        return orchestrator

    def state(self) -> ResearchState:
        return self.store.load()

    def run(self, iterations: int = 1, queries: Iterable[str] | None = None,
            no_network: bool = False, max_seconds: int = 3600) -> ResearchState:
        if not 1 <= iterations <= 1000 or max_seconds < 1:
            raise ValueError("Iterations must be 1..1000 and max_seconds must be positive")
        state = self.state()
        deadline = time.monotonic() + max_seconds
        query_list = None if queries is None else list(queries)
        for _ in range(iterations):
            if time.monotonic() >= deadline:
                self.store.save(state, "budget_exhausted")
                break
            state.iteration += 1
            self._plan(state)
            if not no_network:
                self._literature(state, [state.topic, state.question] if query_list is None else query_list)
            self._hypothesize(state)
            self._validate(state)
            state.stage = "manuscript"
            state.paper_draft = self.writer.write(state)
            self.store.save(state, "iteration_complete", {"sources": len(state.sources), "claims": len(state.claims)})
        return state

    def execute(self, hypothesis_id: str, argv: list[str], seed: int | None = None) -> ResearchState:
        state = self.state()
        hypothesis = next((h for h in state.hypotheses if h.hypothesis_id == hypothesis_id), None)
        if hypothesis is None:
            raise ValueError(f"Unknown hypothesis: {hypothesis_id}")
        experiment = ExperimentRecord(
            experiment_id=stable_id("exp", f"{state.run_id}:{hypothesis_id}:{len(state.experiments)}"),
            hypothesis_id=hypothesis_id, command=argv, seed=seed, status="running", started_at=utc_now(),
        )
        state.experiments.append(experiment)
        self.store.save(state, "experiment_started", {"experiment_id": experiment.experiment_id, "argv": argv})
        outcome = self.executor.run(argv, self.store.artifacts_dir)
        experiment.status = outcome.status  # type: ignore[assignment]
        experiment.stdout, experiment.stderr = outcome.stdout, outcome.stderr
        experiment.finished_at = utc_now()
        self.store.save(state, "experiment_finished", {"experiment_id": experiment.experiment_id, "status": outcome.status})
        return state

    def validate(self) -> list[str]:
        state = self.state()
        errors = self.gate.validate(state)
        self.store.save(state, "evidence_validation", {"errors": errors})
        return errors

    def _plan(self, state: ResearchState) -> None:
        state.stage = "planning"
        state.notes.append(f"Iteration {state.iteration}: scope fixed to the question; no unsupported claim may enter the paper.")
        self.store.save(state, "plan_updated")

    def _literature(self, state: ResearchState, queries: list[str]) -> None:
        state.stage = "literature"
        for query in [q.strip() for q in queries if q.strip()][:4]:
            try:
                new_sources = search_both(query, limit=6)
                state.sources = merge_sources(state.sources, new_sources)
                self.store.save(state, "literature_query", {"query": query, "added": len(new_sources)})
            except RetrievalError as exc:
                state.notes.append(f"Literature retrieval failed for {query!r}: {exc}")
                self.store.save(state, "literature_query_failed", {"query": query, "error": str(exc)})

    def _hypothesize(self, state: ResearchState) -> None:
        state.stage = "hypothesis"
        tree = ResearchTree.from_list(state.search_tree)
        tree.expand_default(state.topic, state.question)
        state.search_tree = tree.to_list()
        if state.hypotheses:
            self.store.save(state, "tree_search_updated", {"nodes": len(tree.nodes)})
            return
        context = "; ".join(s.title for s in state.sources[:5])
        rationale = f"Derived from the research question and retrieved literature: {context or 'no literature was available'}"
        for node in tree.nodes[1:]:
            state.hypotheses.append(Hypothesis(
                hypothesis_id=stable_id("hyp", node.node_id),
                statement=node.statement,
                rationale=rationale,
                predictions=["The pre-registered metric changes relative to a baseline.", "The result survives at least three independent seeds or replications."],
                parent_id=stable_id("hyp", node.parent_id) if node.parent_id else None,
            ))
        self.store.save(state, "hypotheses_proposed", {"count": len(state.hypotheses), "tree_nodes": len(tree.nodes)})

    def _validate(self, state: ResearchState) -> None:
        state.stage = "validation"
        # A source-backed claim is still only a candidate until the source is inspected.
        for source in state.sources[:10]:
            claim_id = stable_id("claim", source.source_id)
            if any(c.claim_id == claim_id for c in state.claims):
                continue
            state.claims.append(Claim(
                claim_id=claim_id,
                statement=f"The source '{source.title}' is relevant to the topic and should be inspected for primary evidence.",
                status="unverified",
                source_ids=[source.source_id],
                confidence=0.25,
                notes="Relevance is not proof of the source's conclusions.",
            ))
        self.gate.validate(state)
        self.store.save(state, "validation_complete", {"errors": state.validation_errors})

    @staticmethod
    def status_text(state: ResearchState) -> str:
        return (
            f"{state.run_id}: stage={state.stage}, iteration={state.iteration}, "
            f"sources={len(state.sources)}, claims={len(state.claims)}, "
            f"hypotheses={len(state.hypotheses)}, experiments={len(state.experiments)}, "
            f"validation_errors={len(state.validation_errors)}"
        )
