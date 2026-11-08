"""Persistent decision controller used by the native EdgeX researcher agent.

The host model proposes actions and performs work. This controller owns the
decision/observation protocol, not the host's permissions or scientific truth.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
import hashlib
import json
import math
import os
import re
import uuid

from .models import utc_now
from .store import RunStore


class ResearchError(ValueError):
    pass


ACTIONS = {
    "frame": ("architect", set(), "framed"),
    "search": ("scout", {"framed"}, "sourced"),
    "design": ("architect", {"sourced"}, "designed"),
    "build": ("builder", {"designed"}, "built"),
    "execute": ("executor", {"built"}, "executed"),
    "analyze": ("statistician", {"sourced"}, "analyzed"),
    "review": ("referee", {"analyzed"}, "reviewed"),
    "replicate": ("reproducibility", {"reviewed"}, "replicated"),
    "write": ("scribe", {"reviewed"}, "written"),
    "complete": ("orchestrator", {"written", "reviewed"}, "completed"),
}
PROFILES = {
    "empirical": {"framed", "sourced", "designed", "built", "executed", "analyzed", "reviewed", "replicated", "written"},
    "theoretical": {"framed", "sourced", "designed", "built", "analyzed", "reviewed", "replicated", "written"},
    "literature": {"framed", "sourced", "analyzed", "reviewed", "written"},
}
ORDER = ["framed", "sourced", "designed", "built", "executed", "analyzed", "reviewed", "replicated", "written"]


def _text(value: Any, label: str, limit: int = 12000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ResearchError(f"{label} must be nonempty text of at most {limit} characters")
    return value.strip()


class ResearchController:
    def __init__(self, root: Path):
        self.root = Path(root).expanduser().resolve()

    def _store(self, run_id: str) -> RunStore:
        if not isinstance(run_id, str) or not re.fullmatch(r"research_[0-9a-f]{24}", run_id):
            raise ResearchError("Invalid research run ID")
        path = self.root / run_id
        if path.is_symlink() or not path.is_dir():
            raise ResearchError("Unknown research run")
        if (path / "artifacts").is_symlink() or (path / "agent.json").is_symlink():
            raise ResearchError("Research state and artifact roots cannot be symlinks")
        return RunStore(path)

    def _load(self, store: RunStore) -> dict:
        return json.loads((store.run_dir / "agent.json").read_text(encoding="utf-8"))

    def _save(self, store: RunStore, state: dict, event: str) -> None:
        state["revision"] += 1
        state["updated_at"] = utc_now()
        tmp = store.run_dir / "agent.json.tmp"
        with tmp.open("w", encoding="utf-8") as stream:
            json.dump(state, stream, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, store.run_dir / "agent.json")
        with (store.run_dir / "agent-events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"event": event, "revision": state["revision"], "at": utc_now()}) + "\n")

    def start(self, question: str, criteria: list[str], max_steps: int = 40,
              max_seconds: int = 7200, profile: str = "empirical") -> dict:
        question = _text(question, "question")
        if not isinstance(criteria, list) or not 1 <= len(criteria) <= 30:
            raise ResearchError("Supply 1..30 measurable acceptance criteria")
        criteria = [_text(c, "criterion", 2000) for c in criteria]
        if len(set(criteria)) != len(criteria):
            raise ResearchError("Acceptance criteria must be distinct")
        if type(max_steps) is not int or not 1 <= max_steps <= 10000:
            raise ResearchError("max_steps must be 1..10000")
        if type(max_seconds) is not int or not 1 <= max_seconds <= 2592000:
            raise ResearchError("max_seconds must be 1..2592000")
        if not isinstance(profile, str) or profile not in PROFILES:
            raise ResearchError("Unknown research profile")
        run_id = "research_" + uuid.uuid4().hex[:24]
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / run_id
        path.mkdir(exist_ok=False)
        store = RunStore(path)
        now = datetime.now(timezone.utc)
        state = dict(run_id=run_id, agent="EdgeX-Researcher", question=question, profile=profile,
                     revision=0, created_at=now.isoformat(), status="active", milestones=[],
                     criteria=[{"id": f"criterion_{i+1}", "text": c, "accepted": False} for i,c in enumerate(criteria)],
                     budget={"max_steps": max_steps, "used_steps": 0,
                             "deadline": (now + timedelta(seconds=max_seconds)).isoformat()},
                     decisions=[], pending=None, observations=[], artifacts={}, evidence={},
                     last_producer=None, recovery_notes=[])
        with store.exclusive():
            self._save(store, state, "started")
        return self.status(run_id)

    def _revision(self, state: dict, revision: int) -> None:
        if type(revision) is not int or revision != state["revision"]:
            raise ResearchError(f"Stale revision; read current status (revision {state['revision']})")

    def _integrity(self, store: RunStore, state: dict) -> None:
        root = store.artifacts_dir.resolve()
        for relative, item in state["artifacts"].items():
            path = (root / relative).resolve()
            if (not path.is_relative_to(root) or not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]):
                raise ResearchError(f"Artifact integrity failed: {relative}; restore reviewed bytes or start a new run")

    def _allowed(self, state: dict) -> dict[str, str]:
        achieved = set(state["milestones"])
        allowed = {}
        for action, (role, required, _) in ACTIONS.items():
            needed = set(required)
            if action == "analyze":
                needed |= {"executed"} if state["profile"] == "empirical" else ({"built"} if state["profile"] == "theoretical" else set())
            if action == "write" and state["profile"] != "literature":
                needed.add("replicated")
            if action == "complete":
                needed |= PROFILES[state["profile"]]
                if not all(c["accepted"] for c in state["criteria"]):
                    continue
            if needed <= achieved:
                allowed[action] = role
        return allowed

    def status(self, run_id: str) -> dict:
        store = self._store(run_id)
        with store.exclusive():
            state = self._load(store)
            self._integrity(store, state)
            seconds = max(0, (datetime.fromisoformat(state["budget"]["deadline"]) - datetime.now(timezone.utc)).total_seconds())
            remaining = state["budget"]["max_steps"] - state["budget"]["used_steps"]
            return dict(run_id=run_id, agent=state["agent"], question=state["question"],
                        profile=state["profile"], revision=state["revision"], status=state["status"],
                        missing_milestones=sorted(PROFILES[state["profile"]] - set(state["milestones"])),
                        milestones=state["milestones"], criteria=state["criteria"],
                        steps_remaining=remaining, seconds_remaining=round(seconds, 2),
                        allowed_actions=self._allowed(state) if state["status"] == "active" and remaining > 0 and seconds > 0 else {},
                        pending=self._decision_preview(state["pending"]), recent_observations=state["observations"][-3:],
                        recent_decisions=[self._decision_preview(d) for d in state["decisions"][-3:]],
                        artifact_manifest=dict(list(state["artifacts"].items())[-50:]),
                        artifacts_omitted=max(0, len(state["artifacts"])-50),
                        evidence_ids=list(state["evidence"])[-100:], recovery_notes=state["recovery_notes"][-5:],
                        canonical_state=str(store.run_dir / "agent.json"),
                        artifacts_directory=str(store.artifacts_dir),
                        decision_policy="Host-proposed candidates; 0.4*information_gain + 0.3*impact + 0.2*feasibility - 0.15*cost - 0.25*risk. Scores are judgment estimates, not measured probabilities.")

    @staticmethod
    def _decision_preview(decision: dict | None) -> dict | None:
        if decision is None:
            return None
        return {key: value for key, value in decision.items() if key != "input_snapshot"}

    def decide(self, run_id: str, revision: int, candidates: list[dict]) -> dict:
        store = self._store(run_id)
        with store.exclusive():
            state = self._load(store)
            self._revision(state, revision)
            self._integrity(store, state)
            if state["status"] != "active":
                raise ResearchError("Research run is complete")
            if state["pending"]:
                raise ResearchError("Observe the pending decision before dispatching more work")
            if state["budget"]["used_steps"] >= state["budget"]["max_steps"] or datetime.now(timezone.utc) >= datetime.fromisoformat(state["budget"]["deadline"]):
                raise ResearchError("Research budget exhausted; preserve results and return a continuation")
            if not isinstance(candidates, list) or not 2 <= len(candidates) <= 8:
                raise ResearchError("Compare 2..8 candidate next actions")
            allowed = self._allowed(state)
            known_refs = set(state["artifacts"]) | set(state["evidence"])
            scored = []
            for candidate in candidates:
                if not isinstance(candidate, dict) or candidate.get("action") not in allowed:
                    raise ResearchError("Candidate action has unmet prerequisites or an unknown action")
                item = {"action": candidate["action"], "role": allowed[candidate["action"]]}
                for key in ("objective", "rationale"):
                    item[key] = _text(candidate.get(key), key, 4000)
                for key in ("information_gain", "impact", "feasibility", "cost", "risk"):
                    number = candidate.get(key)
                    if type(number) not in (int, float) or not math.isfinite(number) or not 0 <= number <= 1:
                        raise ResearchError(f"{key} must be a finite number in [0,1]")
                    item[key] = number
                refs = candidate.get("evidence_refs")
                if not isinstance(refs, list) or any(not isinstance(r, str) or r not in known_refs for r in refs):
                    raise ResearchError("Candidate evidence references must resolve to known evidence or artifact paths")
                item["evidence_refs"] = refs
                if state["observations"]:
                    last = state["observations"][-1]
                    previous = state["decisions"][-1]["selected"]
                    if last["outcome"] != "success" and (item["action"], item["objective"]) == (previous["action"], previous["objective"]):
                        raise ResearchError("Revise the failed objective before repeating it")
                item["score"] = round(.4*item["information_gain"] + .3*item["impact"] + .2*item["feasibility"] - .15*item["cost"] - .25*item["risk"], 6)
                scored.append(item)
            identities = {(c["action"], c["objective"]) for c in scored}
            if len(identities) != len(scored):
                raise ResearchError("Candidates must be distinct alternatives")
            scored.sort(key=lambda c: c["score"], reverse=True)
            selected = scored[0]
            decision = dict(decision_id="decision_"+uuid.uuid4().hex[:16], selected=selected,
                            alternatives=scored[1:], based_on_revision=revision, created_at=utc_now(),
                            input_snapshot={p: a["sha256"] for p,a in state["artifacts"].items()},
                            next_action=f"Dispatch {selected['role']}: {selected['objective']}; return an observation with actual artifacts.")
            state["decisions"].append(decision)
            state["pending"] = decision
            state["budget"]["used_steps"] += 1
            self._save(store, state, "decision_committed")
            result_revision = state["revision"]
        return dict(run_id=run_id, revision=result_revision, decision=decision,
                    artifacts_directory=str(store.artifacts_dir))

    def observe(self, run_id: str, revision: int, decision_id: str, actor: str, outcome: str,
                observation: str, artifacts: list[str], evidence: list[dict] | None = None,
                criteria_ids: list[str] | None = None) -> dict:
        store = self._store(run_id)
        with store.exclusive():
            state = self._load(store)
            self._revision(state, revision)
            self._integrity(store, state)
            pending = state["pending"]
            if not pending or pending["decision_id"] != decision_id:
                raise ResearchError("No matching pending decision")
            actor = _text(actor, "actor", 200)
            observation = _text(observation, "observation")
            if outcome not in ("success", "failure", "inconclusive", "contradiction"):
                raise ResearchError("Unknown observation outcome")
            action = pending["selected"]["action"]
            if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= 30:
                raise ResearchError("Return 1..30 actual artifacts, including for failed work")
            returned = {}
            for relative in artifacts:
                if not isinstance(relative, str):
                    raise ResearchError("Artifact paths must be strings")
                path = (store.artifacts_dir / relative).resolve()
                if not path.is_relative_to(store.artifacts_dir.resolve()) or not path.is_file():
                    raise ResearchError("Artifacts must be existing files inside this run's artifacts directory")
                normalized = path.relative_to(store.artifacts_dir.resolve()).as_posix()
                if normalized in state["artifacts"]:
                    raise ResearchError("Use a new immutable artifact path for each result")
                returned[normalized] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                            actor=actor, action=action, decision_id=decision_id)
            evidence = [] if evidence is None else evidence
            criteria_ids = [] if criteria_ids is None else criteria_ids
            if not isinstance(evidence, list) or not isinstance(criteria_ids, list):
                raise ResearchError("Evidence and criteria IDs must be arrays")
            new_evidence = {}
            for entry in evidence:
                if not isinstance(entry, dict):
                    raise ResearchError("Evidence entries must be objects")
                item = {key: _text(entry.get(key), key, 8000) for key in ("id", "source_url", "excerpt", "locator")}
                if not item["source_url"].startswith("https://") or item["id"] in state["evidence"] or item["id"] in new_evidence:
                    raise ResearchError("Evidence needs an HTTPS source and a fresh ID")
                new_evidence[item["id"]] = item
            if action == "search" and outcome == "success" and not (state["evidence"] or new_evidence):
                raise ResearchError("Successful literature search needs located primary-source evidence")
            known_criteria = {c["id"] for c in state["criteria"]}
            if any(not isinstance(c, str) or c not in known_criteria for c in criteria_ids):
                raise ResearchError("Unknown acceptance criterion")
            if criteria_ids and (action != "review" or outcome != "success"):
                raise ResearchError("Only successful independent review can accept criteria")
            if action in ("review", "replicate") and outcome == "success":
                producers = {a["actor"] for a in state["artifacts"].values() if a["action"] not in ("review", "replicate")}
                if actor in producers:
                    raise ResearchError("Review and replication need a distinct actor label from producers")
            if action == "complete" and outcome != "success":
                raise ResearchError("Completion needs a successful acceptance record")
            state["artifacts"].update(returned)
            state["evidence"].update(new_evidence)
            record = dict(decision_id=decision_id, action=action, actor=actor, outcome=outcome,
                          observation=observation, artifacts=list(returned), evidence_ids=list(new_evidence), at=utc_now())
            state["observations"].append(record)
            milestones = set(state["milestones"])
            if outcome == "success":
                milestones.add(ACTIONS[action][2])
                # Every new producer result invalidates downstream conclusions.
                if action not in ("review", "replicate", "complete"):
                    point = ORDER.index(ACTIONS[action][2])
                    milestones -= set(ORDER[point+1:])
                    milestones.discard("reviewed")
                    for criterion in state["criteria"]:
                        criterion["accepted"] = False
                    state["last_producer"] = actor
                if action == "review":
                    for criterion in state["criteria"]:
                        if criterion["id"] in criteria_ids:
                            criterion["accepted"] = True
                if action == "complete":
                    state["status"] = "completed"
            else:
                if action != "complete":
                    point = ORDER.index(ACTIONS[action][2])
                    milestones -= set(ORDER[point:])
                milestones.discard("reviewed")
                for criterion in state["criteria"]:
                    criterion["accepted"] = False
                state["recovery_notes"].append(f"{outcome} during {action}: {observation}. Revise alternatives; do not repeat an unchanged failed action.")
            state["milestones"] = sorted(milestones)
            state["pending"] = None
            self._save(store, state, "observation_recorded")
        return self.status(run_id)
