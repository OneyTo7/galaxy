from __future__ import annotations

import pathlib
import tempfile

import docker

from app.contexts.evaluation.schemas import CaseResult

_IMAGE = "python:3.12-slim"
_MEM_LIMIT = "128m"
_CPU_QUOTA = 50000
_TIMEOUT = 5


def run_python_docker(code: str, test_cases: list) -> list[CaseResult]:
    client = docker.from_env()
    results: list[CaseResult] = []
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "sol.py").write_text(code)
        for tc in test_cases:
            inp = root / f"input_{tc.id}.txt"
            inp.write_text(tc.input)
            try:
                container = client.containers.run(
                    _IMAGE,
                    command=f"sh -c 'python /code/sol.py < /code/input_{tc.id}.txt'",
                    volumes={str(root): {"bind": "/code", "mode": "rw"}},
                    mem_limit=_MEM_LIMIT,
                    cpu_quota=_CPU_QUOTA,
                    network_mode="none",
                    detach=True,
                )
                try:
                    container.wait(timeout=_TIMEOUT)
                    logs = container.logs().decode("utf-8", errors="replace")
                    timed_out = False
                except Exception:
                    container.kill()
                    logs = ""
                    timed_out = True
                finally:
                    container.remove(force=True)
                passed = (not timed_out) and logs.strip() == tc.expected_output.strip()
                results.append(
                    CaseResult(
                        tc.id, passed, logs,
                        "" if not timed_out else "timeout",
                        timed_out, _TIMEOUT * 1000,
                    )
                )
            except Exception as e:
                results.append(CaseResult(tc.id, False, "", str(e), False, 0))
    return results
