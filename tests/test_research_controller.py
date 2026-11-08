from pathlib import Path
import hashlib
import json

import pytest

from edgex.research_controller import ResearchController, ResearchError


def candidate(action, objective="Investigate the principal evidence gap", quality=0.8):
    return dict(action=action, objective=objective, rationale="Resolve a specific research uncertainty",
                information_gain=quality, impact=quality, feasibility=quality,
                cost=0.1, risk=0.1, evidence_refs=[])


def candidates(action):
    return [candidate(action), candidate(action, "Compare a distinct alternative approach", .4)]


@pytest.fixture
def run(tmp_path):
    c = ResearchController(tmp_path)
    return c, c.start("Does a located source support the bounded claim?", ["Central claim is checked"], profile="literature")


def step(c, status, action, actor="worker", outcome="success", accept=False):
    decision = c.decide(status["run_id"], status["revision"], candidates(action))
    path = Path(decision["artifacts_directory"]) / f"{decision['decision']['decision_id']}.md"
    path.write_text(f"{action}: actual test artifact", encoding="utf-8")
    evidence = [dict(id="source_1", source_url="https://example.org/paper", excerpt="Primary content", locator="section 2")] if action == "search" else []
    return c.observe(status["run_id"], decision["revision"], decision["decision"]["decision_id"],
                     actor, outcome, "Observed result from test fixture", [path.name], evidence,
                     ["criterion_1"] if accept else [])


def test_decisions_are_ranked_and_pending_survives_restart(run, tmp_path):
    c, s = run
    d = c.decide(s["run_id"], s["revision"], candidates("frame"))
    assert d["decision"]["selected"]["score"] > d["decision"]["alternatives"][0]["score"]
    restored = ResearchController(tmp_path).status(s["run_id"])
    assert restored["pending"]["decision_id"] == d["decision"]["decision_id"]
    with pytest.raises(ResearchError, match="pending"):
        c.decide(s["run_id"], restored["revision"], candidates("frame"))
    with pytest.raises(ResearchError, match="Stale"):
        c.decide(s["run_id"], s["revision"], candidates("frame"))


def test_cannot_skip_prerequisites_or_manufacture_reference(run):
    c, s = run
    with pytest.raises(ResearchError, match="prerequisites"):
        c.decide(s["run_id"], s["revision"], candidates("complete"))
    proposal = candidates("frame")
    proposal[0]["evidence_refs"] = ["invented_source"]
    with pytest.raises(ResearchError, match="references"):
        c.decide(s["run_id"], s["revision"], proposal)


def test_budget_and_bad_scores_are_enforced(tmp_path):
    c = ResearchController(tmp_path)
    s = c.start("Question", ["Criterion"], max_steps=1)
    bad = candidates("frame")
    bad[0]["impact"] = float("nan")
    with pytest.raises(ResearchError, match="finite"):
        c.decide(s["run_id"], s["revision"], bad)
    s = step(c, s, "frame")
    with pytest.raises(ResearchError, match="budget"):
        c.decide(s["run_id"], s["revision"], candidates("search"))


def test_complete_needs_fresh_review_after_writing(run):
    c, s = run
    for action in ("frame", "search", "analyze"):
        s = step(c, s, action)
    s = step(c, s, "review", actor="independent-reviewer", accept=True)
    s = step(c, s, "write", actor="writer")
    assert not s["criteria"][0]["accepted"]
    assert "complete" not in s["allowed_actions"]
    s = step(c, s, "review", actor="independent-reviewer", accept=True)
    assert "complete" in s["allowed_actions"]
    s = step(c, s, "complete", actor="coordinator")
    assert s["status"] == "completed"
    assert not s["allowed_actions"]


def test_failure_invalidates_acceptance_and_requires_new_objective(run):
    c, s = run
    for action in ("frame", "search", "analyze"):
        s = step(c, s, action)
    s = step(c, s, "review", actor="reviewer", outcome="contradiction")
    assert "reviewed" not in s["milestones"]
    assert "analyzed" in s["milestones"]
    assert s["recovery_notes"]
    # Once a failed action becomes eligible again, unchanged work is still rejected.
    assert not any(x["accepted"] for x in s["criteria"])


def test_self_review_rejected_and_integrity_checked(run):
    c, s = run
    for action in ("frame", "search", "analyze"):
        s = step(c, s, action)
    with pytest.raises(ResearchError, match="distinct actor"):
        step(c, s, "review", actor="worker")
    path = Path(s["artifacts_directory"]) / next(iter(s["artifact_manifest"]))
    path.write_text("modified after review", encoding="utf-8")
    with pytest.raises(ResearchError, match="integrity"):
        c.status(s["run_id"])


def test_path_traversal_and_unknown_runs_are_rejected(run):
    c, s = run
    with pytest.raises(ResearchError, match="Invalid"):
        c.status("../../config")
    d = c.decide(s["run_id"], s["revision"], candidates("frame"))
    with pytest.raises(ResearchError, match="inside"):
        c.observe(s["run_id"], d["revision"], d["decision"]["decision_id"], "worker", "success", "Reported output", ["../agent.json"])


def test_theory_and_empirical_analysis_cannot_skip_actual_work(tmp_path):
    c = ResearchController(tmp_path)
    for profile in ("theoretical", "empirical"):
        s = c.start("Question", ["Criterion"], profile=profile)
        s = step(c, s, "frame")
        s = step(c, s, "search")
        assert "analyze" not in s["allowed_actions"]
