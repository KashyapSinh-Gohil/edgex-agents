import os
import sys

import pytest

from edgex.execution import ExperimentExecutor


def test_executor_does_not_forward_api_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-a-real-key")
    result = ExperimentExecutor(10).run(
        [sys.executable, "-c", "import os; print('OPENAI_API_KEY' in os.environ)"], tmp_path)
    assert result.status == "completed"
    assert result.stdout.strip() == "False"


@pytest.mark.skipif(os.name != "posix", reason="POSIX signal handling")
def test_timeout_kills_process_ignoring_sigterm(tmp_path):
    result = ExperimentExecutor(1).run(
        [sys.executable, "-c", "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)"], tmp_path)
    assert result.status == "timed_out"
    assert result.elapsed_seconds < 10
