from __future__ import annotations

import argparse
from pathlib import Path
import sys
import json

from .coordination import TaskBoard, ROLES, context_packet
from .store import RunStore

from .pipeline import EdgeXOrchestrator
from .providers import DeterministicModel, OpenAICompatibleModel


def _orchestrator(run_dir: str, offline: bool) -> EdgeXOrchestrator:
    model = DeterministicModel() if offline else OpenAICompatibleModel()
    return EdgeXOrchestrator(run_dir, model=model)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edgex", description="EdgeX evidence-gated research agents")
    parser.add_argument("--version", action="version", version="EdgeX Agents 0.3.0")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a resumable research run")
    init.add_argument("topic")
    init.add_argument("--question", required=True)
    init.add_argument("--run-dir", default="runs/edgex")

    run = sub.add_parser("run", help="advance planning, literature, hypotheses, validation, and paper stages")
    run.add_argument("run_dir")
    run.add_argument("--iterations", type=int, default=1)
    run.add_argument("--query", action="append", dest="queries")
    run.add_argument("--offline", action="store_true", help="skip model and network calls")
    run.add_argument("--no-network", action="store_true", help="skip literature retrieval")
    run.add_argument("--max-seconds", type=int, default=3600, help="iteration scheduling budget; in-flight calls have their own timeouts")

    status = sub.add_parser("status", help="show current run status")
    status.add_argument("run_dir")

    validate = sub.add_parser("validate", help="run the provenance gate")
    validate.add_argument("run_dir")

    paper = sub.add_parser("paper", help="write the current manuscript draft to disk")
    paper.add_argument("run_dir")
    paper.add_argument("--offline", action="store_true")

    install = sub.add_parser("install", help="install the complete skill team into a project")
    install.add_argument("--target", choices=["codex", "claude", "cursor", "copilot", "generic", "all"], default="all")
    install.add_argument("--project", type=Path, default=Path.cwd())
    install.add_argument("--dry-run", action="store_true")

    context = sub.add_parser("context", help="export bounded resume context")
    context.add_argument("run_dir")
    context.add_argument("--max-chars", type=int, default=12000)

    tasks = sub.add_parser("task", help="coordinate host subagents with explicit handoffs")
    tasks.add_argument("run_dir")
    task_sub = tasks.add_subparsers(dest="task_action", required=True)
    task_sub.add_parser("list")
    add = task_sub.add_parser("add")
    add.add_argument("role", choices=ROLES)
    add.add_argument("objective")
    add.add_argument("--accept", action="append", required=True)
    add.add_argument("--input", action="append", default=[])
    add.add_argument("--depends-on", action="append", default=[])
    claim = task_sub.add_parser("claim")
    claim.add_argument("task_id")
    claim.add_argument("--owner", required=True)
    claim.add_argument("--lease-seconds", type=int, default=1800)
    finish = task_sub.add_parser("finish")
    finish.add_argument("task_id")
    finish.add_argument("--owner", required=True)
    finish.add_argument("--output", action="append", default=[])
    finish.add_argument("--evidence", action="append", default=[])
    finish.add_argument("--blocker", action="append", default=[])
    review = task_sub.add_parser("review")
    review.add_argument("task_id")
    review.add_argument("--reviewer", required=True)
    review.add_argument("--accept", action="store_true")
    review.add_argument("--reason", required=True)
    unblock = task_sub.add_parser("unblock")
    unblock.add_argument("task_id")
    unblock.add_argument("--resolution", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "install":
            from .installer import install_package
            paths = install_package(args.target, args.project, args.dry_run)
            print(json.dumps({"dry_run": args.dry_run, "files": paths}, indent=2))
            return 0
        with RunStore(args.run_dir).exclusive():
            return dispatch(args)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"EdgeX: {exc}", file=sys.stderr)
        return 2


def dispatch(args: argparse.Namespace) -> int:
    if args.command == "init":
        EdgeXOrchestrator.create(args.topic, args.question, args.run_dir)
        print(f"Created EdgeX run at {Path(args.run_dir).resolve()}")
        return 0
    if args.command == "status":
        orchestrator = EdgeXOrchestrator(args.run_dir)
        print(orchestrator.status_text(orchestrator.state()))
        return 0
    orchestrator = _orchestrator(args.run_dir, getattr(args, "offline", False))
    if args.command == "context":
        print(context_packet(orchestrator.state(), args.max_chars))
        return 0
    if args.command == "task":
        board = TaskBoard(orchestrator.store)
        if args.task_action == "list":
            result = orchestrator.state().tasks
        elif args.task_action == "add":
            result = board.add(args.role, args.objective, args.accept, args.input, depends_on=args.depends_on)
        elif args.task_action == "claim":
            result = board.claim(args.task_id, args.owner, args.lease_seconds)
        elif args.task_action == "finish":
            result = board.finish(args.task_id, args.owner, args.output, args.evidence, args.blocker)
        elif args.task_action == "unblock":
            result = board.unblock(args.task_id, args.resolution)
        else:
            result = board.review(args.task_id, args.reviewer, args.accept, args.reason)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "run":
        state = orchestrator.run(args.iterations, args.queries,
                                 no_network=args.offline or args.no_network, max_seconds=args.max_seconds)
        print(orchestrator.status_text(state))
        return 0
    if args.command == "validate":
        errors = orchestrator.validate()
        print("Evidence structure: PASS (semantic truth still requires review)" if not errors else "Evidence structure: NOT READY\n" + "\n".join(errors))
        return 0 if not errors else 2
    if args.command == "paper":
        state = orchestrator.state()
        state.paper_draft = orchestrator.writer.write(state)
        output = orchestrator.store.run_dir / "paper_draft.md"
        output.write_text(state.paper_draft + "\n", encoding="utf-8")
        orchestrator.store.save(state, "paper_exported", {"path": str(output)})
        print(output.resolve())
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
