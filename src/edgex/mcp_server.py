"""Dependency-free MCP transport; the controller owns all persistent run state."""
from __future__ import annotations

from contextlib import redirect_stdout
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")
MAX_INPUT_BYTES = 1024 * 1024
ACTIONS = ("frame", "search", "design", "build", "execute", "analyze", "review",
           "replicate", "write", "complete")


def _text(maximum: int = 4000, **extra: Any) -> dict:
    return {"type": "string", "minLength": 1, "maxLength": maximum,
            "pattern": r"\S", **extra}


def _array(items: dict, minimum: int = 0, maximum: int = 100) -> dict:
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


def _object(properties: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": properties, "additionalProperties": False,
            "required": list(properties) if required is None else required}


_ID = _text(128, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_REVISION = {"type": "integer", "minimum": 0, "maximum": 2**53 - 1}
_CANDIDATE = _object({
    "action": {"type": "string", "enum": list(ACTIONS)},
    "objective": _text(), "rationale": _text(),
    **{key: {"type": "number", "minimum": 0, "maximum": 1} for key in
       ("information_gain", "impact", "feasibility", "cost", "risk")},
    "evidence_refs": _array(_text(256)),
})
_SCHEMAS = {
    "research_start": _object({
        "question": _text(12000), "criteria": _array(_text(2000), 1, 30),
        "max_steps": {"type": "integer", "minimum": 1, "maximum": 10000, "default": 40},
        "max_seconds": {"type": "integer", "minimum": 1, "maximum": 2592000, "default": 7200},
        "profile": {"type": "string", "enum": ["empirical", "theoretical", "literature"], "default": "empirical"},
    }, ["question", "criteria"]),
    "research_status": _object({"run_id": _ID}),
    "research_decide": _object({
        "run_id": _ID, "revision": _REVISION, "candidates": _array(_CANDIDATE, 2, 8),
    }),
    "research_observe": _object({
        "run_id": _ID, "revision": _REVISION, "decision_id": _ID, "actor": _text(200),
        "outcome": {"type": "string", "enum": ["success", "failure", "inconclusive", "contradiction"]},
        "observation": _text(12000),
        "artifacts": _array(_text(4096, description="Path relative to this run's artifacts directory.",
            pattern=r"^(?![/\\])(?![A-Za-z]:)(?!\.{1,2}(?:/|$))(?!.*[/]\.{1,2}(?:/|$))[^\\\x00]+$"), 1),
        "evidence": {**_array({"type": "object"}), "type": ["array", "null"], "default": None},
        "criteria_ids": {**_array(_text(256)), "type": ["array", "null"], "default": None},
    }, ["run_id", "revision", "decision_id", "actor", "outcome", "observation", "artifacts"]),
}
_DESCRIPTIONS = {
    "research_start": "Start a persistent research run; the controller generates its run_id.",
    "research_status": "Read a research run's current status and revision.",
    "research_decide": "Select a proposed next action at the supplied run revision.",
    "research_observe": "Record an action outcome, artifacts and evidence at the supplied revision.",
}


def _validate(value: Any, schema: dict, location: str = "arguments") -> None:
    kind = schema["type"]
    kinds = kind if isinstance(kind, list) else [kind]
    valid = {"null": value is None, "object": isinstance(value, dict),
             "array": isinstance(value, list), "string": isinstance(value, str),
             "integer": type(value) is int,
             "number": type(value) in (int, float) and math.isfinite(value)}
    if not any(valid[k] for k in kinds):
        raise ValueError(f"{location}: expected {kind}")
    if value is None:
        return
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{location}: expected one of {schema['enum']}")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        if set(schema.get("required", [])) - value.keys():
            raise ValueError(f"{location}: missing required fields")
        if schema.get("additionalProperties") is False and value.keys() - properties.keys():
            raise ValueError(f"{location}: unexpected fields")
        for key in value.keys() & properties.keys():
            _validate(value[key], properties[key], f"{location}.{key}")
    elif isinstance(value, (str, list)):
        lower, upper = ("minLength", "maxLength") if isinstance(value, str) else ("minItems", "maxItems")
        if not schema.get(lower, 0) <= len(value) <= schema.get(upper, sys.maxsize):
            raise ValueError(f"{location}: length outside allowed bounds")
        if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValueError(f"{location}: invalid format")
        if isinstance(value, list):
            for index, item in enumerate(value):
                _validate(item, schema["items"], f"{location}[{index}]")
    elif not schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf):
        raise ValueError(f"{location}: outside allowed bounds")


def _error(request_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle_request(message: Any, controller: Any, *, protocol_version: str = PROTOCOLS[-1]) -> dict | None:
    """Handle one decoded request. Valid notifications return None without execution."""
    if not isinstance(message, dict):
        return _error(None, -32600, "Invalid Request")
    request_id = message.get("id")
    if request_id is not None and type(request_id) not in (int, str):
        return _error(None, -32600, "Invalid request id")
    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return _error(request_id, -32600, "Invalid Request")
    if "id" not in message:
        return None
    method, params = message["method"], message.get("params", {})
    if not isinstance(params, dict):
        return _error(request_id, -32602, "params must be an object")
    if method == "initialize":
        version = params.get("protocolVersion")
        if (not isinstance(version, str) or not isinstance(params.get("capabilities"), dict)
                or not isinstance(params.get("clientInfo"), dict)
                or not all(isinstance(params["clientInfo"].get(k), str) for k in ("name", "version"))):
            return _error(request_id, -32602, "Invalid initialize parameters")
        result = {"protocolVersion": version if version in PROTOCOLS else PROTOCOLS[-1],
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "edgex", "version": "0.4.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": name, "description": _DESCRIPTIONS[name], "inputSchema": schema,
                             "annotations": {"readOnlyHint": name == "research_status",
                                             "openWorldHint": False}}
                            for name, schema in _SCHEMAS.items()]}
    elif method == "tools/call":
        name, arguments = params.get("name"), params.get("arguments", {})
        if not isinstance(name, str) or name not in _SCHEMAS:
            return _error(request_id, -32602, "Unknown tool")
        schema = _SCHEMAS[name]
        try:
            _validate(arguments, schema)
            if len(json.dumps(arguments, allow_nan=False).encode("utf-8")) > MAX_INPUT_BYTES:
                raise ValueError("arguments exceed 1 MiB")
        except (ValueError, TypeError, OverflowError, RecursionError) as exc:
            return _error(request_id, -32602, str(exc))
        arguments = {**{k: v["default"] for k, v in schema["properties"].items() if "default" in v}, **arguments}
        try:
            with redirect_stdout(sys.stderr):
                payload = getattr(controller, name.removeprefix("research_"))(**arguments)
            failed = False
        except ValueError as exc:
            payload, failed = {"error": str(exc)}, True
        except Exception:
            return _error(request_id, -32603, "Internal controller error")
        try:
            if not isinstance(payload, dict):
                raise TypeError("Controller result must be an object")
            result = {"content": [{"type": "text", "text": json.dumps(payload, allow_nan=False)}], "isError": failed}
            if protocol_version == "2025-06-18":
                result["structuredContent"] = payload
        except (TypeError, ValueError, OverflowError, RecursionError):
            return _error(request_id, -32603, "Invalid controller result")
    else:
        return _error(request_id, -32601, "Method not found")
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _reject_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def serve(root: Path) -> None:
    """Serve newline-delimited JSON-RPC on stdin/stdout until EOF; CLI supplies root."""
    with redirect_stdout(sys.stderr):
        from .research_controller import ResearchController
        controller = ResearchController(root)
    version = PROTOCOLS[-1]
    while line := sys.stdin.buffer.readline(MAX_INPUT_BYTES + 1):
        try:
            if len(line) > MAX_INPUT_BYTES:
                while line and not line.endswith(b"\n"):
                    line = sys.stdin.buffer.readline(MAX_INPUT_BYTES + 1)
                print(json.dumps(_error(None, -32600, "Request exceeds 1 MiB")), flush=True)
                continue
            message = json.loads(line.decode("utf-8"), parse_constant=_reject_constant)
        except (ValueError, UnicodeError, RecursionError):
            response = _error(None, -32700, "Parse error")
        else:
            response = handle_request(message, controller, protocol_version=version)
            if isinstance(message, dict) and message.get("method") == "initialize" and response and "result" in response:
                version = response["result"]["protocolVersion"]
        if response is not None:
            print(json.dumps(response, allow_nan=False), flush=True)
