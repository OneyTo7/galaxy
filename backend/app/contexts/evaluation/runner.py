from __future__ import annotations

import pathlib
import subprocess
import tempfile
import time

from app.core.config import settings
from app.contexts.evaluation.lang_config import LANG_CONFIG
from app.contexts.evaluation.schemas import CaseResult

_TIMEOUT = 5


def run(code: str, lang: str, test_cases: list) -> list[CaseResult]:
    if lang not in LANG_CONFIG:
        raise ValueError(f"unsupported lang: {lang}")
    if settings.SANDBOX_MODE == "docker":
        from app.contexts.evaluation.sandbox import run_docker
        return run_docker(code, lang, test_cases)
    return _run_subprocess(code, lang, test_cases)


def _run_subprocess(code: str, lang: str, test_cases: list) -> list[CaseResult]:
    cfg = LANG_CONFIG[lang]
    results: list[CaseResult] = []
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        src = root / cfg["filename"]
        src.write_text(code)
        bin_path = root / "sol"
        if cfg["compile_cmd"]:
            compile_args = [
                a.replace("{src}", str(src)).replace("{bin}", str(bin_path))
                for a in cfg["compile_cmd"]
            ]
            try:
                subprocess.run(compile_args, capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired:
                for tc in test_cases:
                    results.append(CaseResult(tc.id, False, "", "compile timeout", False, 0))
                return results
        for tc in test_cases:
            start = time.monotonic()
            run_args = [
                a.replace("{src}", str(src)).replace("{bin}", str(bin_path)).replace("{dir}", str(root))
                for a in cfg["run_cmd"]
            ]
            try:
                proc = subprocess.run(
                    run_args,
                    input=tc.input,
                    capture_output=True,
                    text=True,
                    timeout=_TIMEOUT,
                )
                elapsed = int((time.monotonic() - start) * 1000)
                expected = tc.expected_output.strip() if tc.expected_output else ""
                actual = proc.stdout.strip()
                if not expected:
                    passed = False
                    results.append(
                        CaseResult(tc.id, False, actual, "expected_output is empty", False, elapsed)
                    )
                else:
                    passed = actual == expected
                    results.append(
                        CaseResult(tc.id, passed, proc.stdout, proc.stderr, False, elapsed)
                    )
            except subprocess.TimeoutExpired:
                results.append(CaseResult(tc.id, False, "", "timeout", True, _TIMEOUT * 1000))
    return results
