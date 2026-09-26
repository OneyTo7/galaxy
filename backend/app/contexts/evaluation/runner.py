from __future__ import annotations

import pathlib
import subprocess
import tempfile
import time

from app.contexts.evaluation.schemas import CaseResult


def run(code: str, lang: str, test_cases: list) -> list[CaseResult]:
    if lang == "python":
        return _run_python(code, test_cases)
    raise ValueError(f"unsupported lang: {lang}")


def _run_python(code: str, test_cases: list) -> list[CaseResult]:
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
