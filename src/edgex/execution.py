from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import os
import signal
import subprocess
import sys
import time


@dataclass
class ExecutionOutcome:
    status: str
    stdout: str
    stderr: str
    elapsed_seconds: float
    returncode: int | None


class ExperimentExecutor:
    """Executes an explicit argv command with bounded time and no shell expansion."""

    def __init__(self, timeout_seconds: int = 3600):
        self.timeout_seconds = timeout_seconds

    def run(self, argv: Sequence[str], cwd: str | Path) -> ExecutionOutcome:
        started = time.monotonic()
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONUNBUFFERED": "1"}
        for key in ("CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
            if key in os.environ:
                env[key] = os.environ[key]
        try:
            process = subprocess.Popen(
                list(argv), cwd=str(cwd), env=env, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=self.timeout_seconds)
                status = "completed" if process.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    stdout, stderr = process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    if os.name == "posix":
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    stdout, stderr = process.communicate(timeout=3)
                stdout = (stdout or "") + "\n[EdgeX timeout]"
                stderr = (stderr or "") + f"\nExceeded {self.timeout_seconds}s"
                status = "timed_out"
            return ExecutionOutcome(status, stdout, stderr, time.monotonic() - started, process.returncode)
        except OSError as exc:
            return ExecutionOutcome("failed", "", str(exc), time.monotonic() - started, None)


def python_command(script: str) -> list[str]:
    return [sys.executable, script]
