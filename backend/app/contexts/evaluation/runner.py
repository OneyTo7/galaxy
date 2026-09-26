from __future__ import annotations

import pathlib
import subprocess
import tempfile
import time

from app.core.config import settings
from app.contexts.evaluation.schemas import CaseResult


def run(code: str, lang: str, test_cases: list) -> list[CaseResult]:
    if lang != "python":
        raise ValueError(f"unsupported lang: {lang}")
    if settings.SANDBOX_MODE == "docker":
        from app.contexts.evaluation.sandbox import run_python_docker
        return run_python_docker(code, test_cases)
    return _run_python_subprocess(code, test_cases)


def _run_python_subprocess(code: str, test_cases: list) -> list[CaseResult]:
    results: list[CaseResult] = []
    with tempfile.TemporaryDirectory() as d:
        src = pathlib.Path(d) / "sol.py"
        src.write_text(code)
        for tc in test_cases:
            start = time.monotonic()
            try:
                proc = subprocess.run(
                    ["python3", str(src)],
                    input=tc.input,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                elapsed = int((time.monotonic() - start) * 1000)
                passed = proc.stdout.strip() == tc.expected_output.strip()
                results.append(
                    CaseResult(tc.id, passed, proc.stdout, proc.stderr, False, elapsed)
                )
            except subprocess.TimeoutExpired:
                results.append(CaseResult(tc.id, False, "", "timeout", True, 5000))
    return results
