from __future__ import annotations

LANG_CONFIG = {
    "python": {
        "filename": "sol.py",
        "compile_cmd": None,
        "run_cmd": ["python3", "{src}"],
        "docker_image": "python:3.12-slim",
        "docker_cmd": "python /code/sol.py",
    },
    "c": {
        "filename": "sol.c",
        "compile_cmd": ["gcc", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "docker_image": "gcc:14-slim",
        "docker_cmd": "sh -c 'gcc -o /code/sol /code/sol.c && /code/sol'",
    },
    "cpp": {
        "filename": "sol.cpp",
        "compile_cmd": ["g++", "-o", "{bin}", "{src}"],
        "run_cmd": ["{bin}"],
        "docker_image": "gcc:14-slim",
        "docker_cmd": "sh -c 'g++ -o /code/sol /code/sol.cpp && /code/sol'",
    },
    "java": {
        "filename": "Sol.java",
        "compile_cmd": ["javac", "{src}"],
        "run_cmd": ["java", "-cp", "{dir}", "Sol"],
        "docker_image": "openjdk:21-slim",
        "docker_cmd": "sh -c 'javac /code/Sol.java && java -cp /code Sol'",
    },
}
