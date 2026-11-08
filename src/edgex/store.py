from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os
from contextlib import contextmanager

from .models import ResearchState, utc_now


class RunStore:
    """Crash-safe snapshots plus an append-only event log for resume/debugging."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_path = self.run_dir / "state.json"
        self.events_path = self.run_dir / "events.jsonl"
        self.artifacts_dir = self.run_dir / "artifacts"
        self.artifacts_dir.mkdir(exist_ok=True)

    def save(self, state: ResearchState, event: str, data: dict[str, Any] | None = None) -> None:
        state.touch()
        tmp_path = self.snapshot_path.with_suffix(".json.tmp")
        tmp_path.write_text(state.json() + "\n", encoding="utf-8")
        os.replace(tmp_path, self.snapshot_path)
        record = {"at": utc_now(), "event": event, "data": data or {}, "stage": state.stage, "iteration": state.iteration}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def load(self) -> ResearchState:
        if not self.snapshot_path.exists():
            raise FileNotFoundError(f"No EdgeX run exists at {self.run_dir}")
        return ResearchState.from_dict(json.loads(self.snapshot_path.read_text(encoding="utf-8")))

    def read_events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        return [json.loads(line) for line in self.events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @contextmanager
    def exclusive(self):
        """OS-released coordinator lock, including after a killed process."""
        with (self.run_dir / ".coordinator.lock").open("a+b") as handle:
            if os.name == "posix":
                import fcntl
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise RuntimeError("Another coordinator owns this run") from exc
                try:
                    yield
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
            else:
                import msvcrt
                handle.write(b"0")
                handle.flush()
                handle.seek(0)
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise RuntimeError("Another coordinator owns this run") from exc
                try:
                    yield
                finally:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
