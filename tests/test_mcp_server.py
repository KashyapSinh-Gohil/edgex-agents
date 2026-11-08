import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from edgex.mcp_server import ACTIONS, MAX_INPUT_BYTES, PROTOCOLS, handle_request


def request(method, params=None, request_id=1):
    return {"jsonrpc": "2.0", "id": request_id, "method": method,
            "params": {} if params is None else params}


def initialize(version):
    return request("initialize", {"protocolVersion": version, "capabilities": {},
                                  "clientInfo": {"name": "test", "version": "1"}})


def candidate():
    return {"action": "frame", "objective": "Define the question", "rationale": "Reduce ambiguity",
            "information_gain": 0.8, "impact": 1, "feasibility": 0.9, "cost": 0.2,
            "risk": 0, "evidence_refs": []}


def candidates():
    return [candidate(), {**candidate(), "objective": "Test an alternative framing"}]


def observe():
    return {"run_id": "run_1", "revision": 1, "decision_id": "decision_1", "actor": "researcher",
            "outcome": "success", "observation": "The question is falsifiable.", "artifacts": ["frame.md"]}


@pytest.fixture
def controller():
    mock = Mock(spec=["start", "status", "decide", "observe"])
    for name in ("start", "status", "decide", "observe"):
        getattr(mock, name).return_value = {"run_id": "run_1", "revision": 1}
    return mock


def call(controller, name, arguments, version=PROTOCOLS[-1]):
    return handle_request(request("tools/call", {"name": name, "arguments": arguments}),
                          controller, protocol_version=version)


@pytest.mark.parametrize("version", [*PROTOCOLS, "2099-01-01"])
def test_initialize_negotiates_supported_protocol(controller, version):
    result = handle_request(initialize(version), controller)["result"]
    assert result["protocolVersion"] == (version if version in PROTOCOLS else PROTOCOLS[-1])
    assert result["capabilities"] == {"tools": {"listChanged": False}}
    assert result["serverInfo"]["name"] == "edgex"
    assert not controller.mock_calls


def test_list_advertises_explicit_schemas(controller):
    tools = {t["name"]: t for t in handle_request(request("tools/list"), controller)["result"]["tools"]}
    assert set(tools) == {"research_start", "research_status", "research_decide", "research_observe"}
    for name, tool in tools.items():
        assert tool["inputSchema"]["additionalProperties"] is False
        assert tool["annotations"]["readOnlyHint"] == (name == "research_status")
        assert tool["annotations"]["openWorldHint"] is False
    start = tools["research_start"]["inputSchema"]
    assert start["required"] == ["question", "criteria"]
    assert start["properties"]["max_steps"]["default"] == 40
    assert start["properties"]["max_seconds"]["default"] == 7200
    assert start["properties"]["profile"]["default"] == "empirical"
    decide = tools["research_decide"]["inputSchema"]["properties"]["candidates"]["items"]
    assert set(decide["required"]) == set(candidate())
    assert decide["properties"]["action"]["enum"] == list(ACTIONS)


@pytest.mark.parametrize("version", PROTOCOLS)
@pytest.mark.parametrize("name,arguments,expected", [
    ("research_start", {"question": "Does it work?", "criteria": ["Reproduce the result"]},
     {"question": "Does it work?", "criteria": ["Reproduce the result"], "max_steps": 40,
      "max_seconds": 7200, "profile": "empirical"}),
    ("research_status", {"run_id": "run_1"}, {"run_id": "run_1"}),
    ("research_decide", {"run_id": "run_1", "revision": 0, "candidates": candidates()},
     {"run_id": "run_1", "revision": 0, "candidates": candidates()}),
    ("research_observe", observe(), {**observe(), "evidence": None, "criteria_ids": None}),
])
def test_tools_forward_arguments_and_return_consistent_content(controller, version, name, arguments, expected):
    result = call(controller, name, arguments, version)["result"]
    getattr(controller, name.removeprefix("research_")).assert_called_once_with(**expected)
    assert result["isError"] is False
    assert json.loads(result["content"][0]["text"]) == {"run_id": "run_1", "revision": 1}
    assert ("structuredContent" in result) == (version == "2025-06-18")
    if "structuredContent" in result:
        assert result["structuredContent"] == json.loads(result["content"][0]["text"])


@pytest.mark.parametrize("profile", ["empirical", "theoretical", "literature"])
def test_start_overrides_defaults(controller, profile):
    args = {"question": "A question", "criteria": ["A criterion"], "max_steps": 2,
            "max_seconds": 15, "profile": profile}
    assert not call(controller, "research_start", args)["result"]["isError"]
    controller.start.assert_called_once_with(**args)


@pytest.mark.parametrize("outcome", ["success", "failure", "inconclusive", "contradiction"])
def test_observe_passes_optional_evidence_unchanged(controller, outcome):
    args = {**observe(), "outcome": outcome, "artifacts": ["metrics/result.json"],
            "evidence": [{"source_id": "source_1", "confidence": 0.8}], "criteria_ids": ["criterion_1"]}
    assert not call(controller, "research_observe", args)["result"]["isError"]
    controller.observe.assert_called_once_with(**args)


@pytest.mark.parametrize("name,args", [
    ("research_start", {}),
    ("research_start", {"question": " ", "criteria": ["criterion"]}),
    ("research_start", {"question": "q", "criteria": []}),
    ("research_start", {"question": "q", "criteria": [3]}),
    *[("research_start", {"question": "q", "criteria": ["c"], key: value})
      for key, value in [("max_steps", 0), ("max_steps", True), ("max_steps", 10001),
                         ("max_seconds", 0), ("max_seconds", 2592001), ("max_seconds", 1.5),
                         ("profile", "unknown"), ("profile", None), ("root", "/tmp/escape"),
                         ("question", "x" * 12001)]],
    ("research_status", {"run_id": "../escape"}),
    ("research_decide", {"run_id": "run_1", "revision": True, "candidates": candidates()}),
    ("research_decide", {"run_id": "run_1", "revision": -1, "candidates": candidates()}),
    ("research_decide", {"run_id": "run_1", "revision": 0, "candidates": []}),
    ("research_decide", {"run_id": "run_1", "revision": 0, "candidates": [candidate()]}),
    ("research_decide", {"run_id": "run_1", "revision": 0, "candidates": candidates() * 5}),
    *[("research_decide", {"run_id": "run_1", "revision": 0,
                           "candidates": [{**candidate(), key: value}, candidates()[1]]})
      for key, value in [("action", "shell"), ("cost", -1), ("risk", 1.1), ("impact", True),
                         ("feasibility", float("nan")), ("information_gain", float("inf")),
                         ("evidence_refs", [1]), ("extra", "unexpected")]],
    *[("research_decide", {"run_id": "run_1", "revision": 0,
                           "candidates": [{k: v for k, v in candidate().items() if k != missing}, candidates()[1]]})
      for missing in candidate()],
    ("research_observe", {**observe(), "revision": False}),
    ("research_observe", {**observe(), "outcome": "passed"}),
    ("research_observe", {**observe(), "evidence": ["source"]}),
    ("research_observe", {**observe(), "criteria_ids": [False]}),
    *[("research_observe", {**observe(), "artifacts": [artifact]}) for artifact in
      ["/tmp/result", "../result", "a/../result", "a/../../result", "./result", "a/..",
       "", ".", "..", "\\escape", "a\\escape", "C:/escape", "a\x00b"]],
    ("research_observe", {**observe(), "artifacts": []}),
    ("research_observe", {k: v for k, v in observe().items() if k != "artifacts"}),
    ("research_observe", {**observe(), "evidence": [{"raw": "x" * MAX_INPUT_BYTES}]}),
])
def test_invalid_tool_arguments_never_reach_controller(controller, name, args):
    response = call(controller, name, args)
    assert response["error"]["code"] == -32602
    assert not controller.mock_calls


@pytest.mark.parametrize("message,code", [
    ([], -32600), (None, -32600), ({}, -32600),
    ({"jsonrpc": "1.0", "id": 1, "method": "ping"}, -32600),
    ({"jsonrpc": "2.0", "id": True, "method": "ping"}, -32600),
    ({"jsonrpc": "2.0", "id": [], "method": "ping"}, -32600),
    (request("unknown"), -32601),
    ({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": []}, -32602),
    (request("initialize"), -32602),
    (request("tools/call", {"name": "unknown"}), -32602),
    (request("tools/call", {"name": []}), -32602),
    (request("tools/call", {"name": "research_status", "arguments": None}), -32602),
])
def test_jsonrpc_errors(controller, message, code):
    assert handle_request(message, controller)["error"]["code"] == code
    assert not controller.mock_calls


def test_ping_ids_and_notifications(controller):
    assert handle_request(request("ping", request_id="ping-1"), controller) == {
        "jsonrpc": "2.0", "id": "ping-1", "result": {}}
    for method in ("notifications/initialized", "notifications/cancelled", "tools/call", "unknown"):
        assert handle_request({"jsonrpc": "2.0", "method": method}, controller) is None
    assert not controller.mock_calls


@pytest.mark.parametrize("version", PROTOCOLS)
def test_research_error_is_a_tool_error(controller, version):
    class ResearchError(ValueError):
        pass

    controller.status.side_effect = ResearchError("Stale revision or missing run")
    response = call(controller, "research_status", {"run_id": "run_1"}, version)
    assert "error" not in response
    result = response["result"]
    assert result["isError"] is True
    assert json.loads(result["content"][0]["text"]) == {"error": "Stale revision or missing run"}
    if version == PROTOCOLS[-1]:
        assert result["structuredContent"] == json.loads(result["content"][0]["text"])


def test_unexpected_errors_and_invalid_results(controller, capsys):
    def noisy_status(**kwargs):
        print("controller diagnostic")
        raise RuntimeError("private implementation details")

    controller.status.side_effect = noisy_status
    response = call(controller, "research_status", {"run_id": "run_1"})
    assert response["error"] == {"code": -32603, "message": "Internal controller error"}
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "controller diagnostic\n"
    controller.status.side_effect = None
    for bad_result in ([], {"score": float("nan")}, {"not_json": object()}):
        controller.status.return_value = bad_result
        assert call(controller, "research_status", {"run_id": "run_1"})["error"]["code"] == -32603


def run_stdio(tmp_path, data):
    # Inject only the controller: exercise the real transport in a separate interpreter.
    program = """
import sys, types
from pathlib import Path
class Controller:
    def __init__(self, root):
        assert root == Path(sys.argv[1])
        print('controller initialized')
    def status(self, run_id):
        print('controller status')
        return {'run_id': run_id, 'revision': 0}
module = types.ModuleType('edgex.research_controller')
module.ResearchController = Controller
sys.modules['edgex.research_controller'] = module
from edgex.mcp_server import serve
serve(Path(sys.argv[1]))
"""
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    return subprocess.run([sys.executable, "-c", program, str(tmp_path)], input=data,
                          capture_output=True, timeout=10, check=True, env=env)


@pytest.mark.parametrize("version", PROTOCOLS)
def test_real_stdio_process_handshake_notifications_and_tool_call(tmp_path, version):
    messages = [initialize(version), {"jsonrpc": "2.0", "method": "notifications/initialized"},
                request("tools/list", request_id=2),
                request("tools/call", {"name": "research_status", "arguments": {"run_id": "run_1"}}, 3),
                request("ping", request_id=4)]
    completed = run_stdio(tmp_path, ("\n".join(json.dumps(m) for m in messages) + "\n").encode())
    responses = [json.loads(line) for line in completed.stdout.splitlines()]
    assert [r["id"] for r in responses] == [1, 2, 3, 4]
    assert responses[0]["result"]["protocolVersion"] == version
    assert len(responses[1]["result"]["tools"]) == 4
    assert ("structuredContent" in responses[2]["result"]) == (version == PROTOCOLS[-1])
    assert responses[3]["result"] == {}
    assert completed.stderr.splitlines() == [b"controller initialized", b"controller status"]


def test_stdio_recovers_after_malformed_and_oversized_messages(tmp_path):
    malformed = [b"{", b"{\"value\":NaN}", b"\xff", b" "]
    oversized = b"x" * (MAX_INPUT_BYTES + 5)
    data = b"\n".join([*malformed, oversized, b"[]", json.dumps(request("ping", request_id=9)).encode()]) + b"\n"
    responses = [json.loads(line) for line in run_stdio(tmp_path, data).stdout.splitlines()]
    assert [r["error"]["code"] for r in responses[:-1]] == [-32700] * 4 + [-32600, -32600]
    assert all(r["id"] is None for r in responses[:-1])
    assert responses[-1] == {"jsonrpc": "2.0", "id": 9, "result": {}}


@pytest.mark.skipif(importlib.util.find_spec("edgex.research_controller") is None,
                    reason="ResearchController is implemented separately")
def test_real_controller_start_and_status(tmp_path):
    from edgex.research_controller import ResearchController

    controller = ResearchController(tmp_path)
    started = call(controller, "research_start", {
        "question": "Can the baseline be independently reproduced?",
        "criteria": ["Record a reproducible baseline"], "profile": "empirical",
    })["result"]
    assert started["isError"] is False, started
    run_id = started["structuredContent"]["run_id"]
    assert isinstance(run_id, str) and run_id
    # A fresh instance must recover the run from the same root.
    status = call(ResearchController(tmp_path), "research_status", {"run_id": run_id})["result"]
    assert status["isError"] is False, status
    assert status["structuredContent"]["run_id"] == run_id
    assert json.loads(status["content"][0]["text"]) == status["structuredContent"]
    state = status["structuredContent"]
    decision = call(controller, "research_decide", {
        "run_id": run_id, "revision": state["revision"], "candidates": candidates(),
    })["result"]
    assert decision["isError"] is False, decision
    committed = decision["structuredContent"]
    artifacts_dir = Path(committed["artifacts_directory"])
    assert artifacts_dir.is_relative_to(tmp_path)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "frame.md").write_text("A falsifiable baseline question.\n", encoding="utf-8")
    result = call(controller, "research_observe", {
        **observe(), "run_id": run_id, "revision": committed["revision"],
        "decision_id": committed["decision"]["decision_id"],
    })["result"]
    assert result["isError"] is False, result
    assert result["structuredContent"]["pending"] is None
    assert "framed" in result["structuredContent"]["milestones"]
    assert "frame.md" in result["structuredContent"]["artifact_manifest"]
    stale = call(controller, "research_decide", {
        "run_id": run_id, "revision": state["revision"], "candidates": candidates(),
    })["result"]
    assert stale["isError"] is True
    assert "Stale revision" in stale["structuredContent"]["error"]
