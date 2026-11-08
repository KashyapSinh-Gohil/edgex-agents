from datetime import datetime, timedelta, timezone
import json

import pytest

from edgex.coordination import TaskBoard, context_packet
from edgex.models import Claim, Evidence, ResearchState, Source
from edgex.pipeline import EdgeXOrchestrator, EvidenceGate, PaperWriter


@pytest.fixture
def run(tmp_path):
    return EdgeXOrchestrator.create("AI", "Does an intervention improve a held-out metric?", tmp_path)


def test_dependencies_independent_review_and_hashes(run):
    board = TaskBoard(run.store)
    task = board.add("scout", "Locate primary evidence", ["A located excerpt is supplied"])
    followup = board.add("referee", "Review findings", ["Check primary sources"], depends_on=[task["task_id"]])
    with pytest.raises(ValueError, match="Dependencies"):
        board.claim(followup["task_id"], "referee-1")
    board.claim(task["task_id"], "scout-1")
    (run.store.artifacts_dir / "findings.md").write_text("Evidence with a locator")
    board.finish(task["task_id"], "scout-1", ["findings.md"], ["src_1"])
    with pytest.raises(ValueError, match="distinct"):
        board.review(task["task_id"], "scout-1", True, "self review")
    (run.store.artifacts_dir / "findings.md").write_text("tampered")
    with pytest.raises(ValueError, match="changed"):
        board.review(task["task_id"], "reviewer-1", True, "reviewed")
    assert board.review(task["task_id"], "reviewer-1", False, "Artifact changed")["status"] == "queued"
    assert board.claim(task["task_id"], "scout-2")["attempts"] == 2


def test_expired_lease_recovery_and_attempt_budget(run):
    board = TaskBoard(run.store)
    task = board.add("builder", "Run baseline", ["Metric available"], max_attempts=2)
    board.claim(task["task_id"], "worker-1")
    state = run.state()
    state.tasks[0]["lease_until"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    run.store.save(state, "simulate_expiry")
    assert board.claim(task["task_id"], "worker-2")["attempts"] == 2
    state = run.state()
    state.tasks[0]["lease_until"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
    run.store.save(state, "simulate_expiry")
    with pytest.raises(ValueError, match="budget"):
        board.claim(task["task_id"], "worker-3")


def test_task_artifact_path_escape_is_rejected(run, tmp_path):
    board = TaskBoard(run.store)
    task = board.add("builder", "Task", ["Evidence"])
    board.claim(task["task_id"], "worker")
    with pytest.raises(ValueError, match="inside artifacts"):
        board.finish(task["task_id"], "worker", ["../state.json"], [])


def test_successful_review_unlocks_dependent_task(run):
    board = TaskBoard(run.store)
    first = board.add("builder", "Build", ["Artifact exists"])
    second = board.add("referee", "Inspect", ["Review artifact"], depends_on=[first["task_id"]])
    board.claim(first["task_id"], "builder-1")
    (run.store.artifacts_dir / "baseline.txt").write_text("baseline evidence")
    returned = board.finish(first["task_id"], "builder-1", ["baseline.txt"], [])
    assert returned["status"] == "review"
    assert len(returned["outputs"][0]["sha256"]) == 64
    assert board.review(first["task_id"], "reviewer-1", True, "Checked output")["status"] == "completed"
    assert board.claim(second["task_id"], "referee-2")["status"] == "running"


def test_context_is_bounded_and_originals_preserved(run):
    state = run.state()
    state.notes = ["long " * 3000 for _ in range(10)]
    packet = context_packet(state, 1000)
    assert len(packet) <= 1000
    assert json.loads(packet)["omitted"] > 0
    assert len(state.notes) == 10


def test_no_empty_research_pass_and_no_source_only_support():
    state = ResearchState.new("topic", "question")
    assert EvidenceGate().validate(state)
    state.sources = [Source("s1", "Paper", "https://example.org")]
    state.claims = [Claim("c1", "Claim", status="supported", source_ids=["s1"])]
    assert EvidenceGate().validate(state)
    assert state.claims[0].status == "unverified"
    state.evidence = [Evidence("e1", "s1", "Located excerpt", locator="section 3", supports=["c1"], reviewed_by="reviewer")]
    state.claims[0].evidence_ids = ["e1"]
    state.claims[0].status = "supported"
    assert EvidenceGate().validate(state) == []


def test_duplicate_init_does_not_overwrite(run):
    before = run.store.snapshot_path.read_bytes()
    with pytest.raises(FileExistsError):
        EdgeXOrchestrator.create("replacement", "replacement", run.store.run_dir)
    assert run.store.snapshot_path.read_bytes() == before
