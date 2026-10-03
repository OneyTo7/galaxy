from __future__ import annotations

import pathlib
import tempfile

import docker

from app.contexts.evaluation.lang_config import LANG_CONFIG
from app.contexts.evaluation.schemas import CaseResult

_MEM_LIMIT = "128m"
_CPU_QUOTA = 50000
_TIMEOUT = 5


def run_docker(code: str, lang: str, test_cases: list) -> list[CaseResult]:
    cfg = LANG_CONFIG[lang]
    client = docker.from_env()
    results: list[CaseResult] = []
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / cfg["filename"]).write_text(code)
        for tc in test_cases:
            inp = root / f"input_{tc.id}.txt"
            inp.write_text(tc.input)
            try:
                container = client.containers.run(
                    cfg["docker_image"],
                    command=f"sh -c '{cfg['docker_cmd']} < /code/input_{tc.id}.txt'",
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
                expected = tc.expected_output.strip() if tc.expected_output else ""
                actual = logs.strip()
                if not expected:
                    passed = False
                    results.append(
                        CaseResult(tc.id, False, actual, "expected_output is empty", False, _TIMEOUT * 1000)
                    )
                else:
                    passed = (not timed_out) and actual == expected
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
