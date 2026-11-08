from pathlib import Path
import json
import subprocess
import sys

from edgex.models import Claim, ResearchState, Source
from edgex.pipeline import EdgeXOrchestrator, EvidenceGate
from edgex.store import RunStore
from edgex.tree_search import ResearchTree


def test_state_round_trip(tmp_path: Path) -> None:
    state = ResearchState.new("edge AI", "Does method X improve robustness?")
    state.sources.append(Source(source_id="src_1", title="Primary study", url="https://example.org/paper"))
    RunStore(tmp_path).save(state, "created")
    loaded = RunStore(tmp_path).load()
    assert loaded.run_id == state.run_id
    assert loaded.sources[0].title == "Primary study"


def test_evidence_gate_downgrades_missing_provenance() -> None:
    state = ResearchState.new("topic", "question")
    state.claims.append(Claim(claim_id="claim_1", statement="unsupported"))
    errors = EvidenceGate().validate(state)
    assert state.claims[0].status == "unverified"
    assert errors


def test_offline_run_is_resumable(tmp_path: Path) -> None:
    orchestrator = EdgeXOrchestrator.create("quantum ML", "Can a stated intervention improve a fixed metric?", tmp_path)
    state = orchestrator.run(iterations=1, queries=[])
    assert state.iteration == 1
    assert len(state.hypotheses) == 3
    assert len(state.search_tree) == 4
    assert (tmp_path / "state.json").exists()
    assert (tmp_path / "events.jsonl").exists()


def test_tree_search_propagates_scores() -> None:
    tree = ResearchTree()
    tree.expand_default("topic", "question")
    node = tree.nodes[-1]
    tree.record(node.node_id, 0.9)
    assert node.mean_value == 0.9
    assert tree.nodes[0].visits == 1


def test_cli_init_status(tmp_path: Path) -> None:
    env = dict(**__import__("os").environ)
    source = Path(__file__).parents[1] / "src"
    env["PYTHONPATH"] = str(source)
    result = subprocess.run(
        [sys.executable, "-m", "edgex", "init", "AI", "--question", "What is reproducible?", "--run-dir", str(tmp_path)],
        env=env, capture_output=True, text=True, check=True,
    )
    assert "Created EdgeX run" in result.stdout
    assert json.loads((tmp_path / "state.json").read_text())["topic"] == "AI"
