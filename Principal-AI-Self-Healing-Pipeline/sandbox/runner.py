import json
import shutil
import subprocess
import tempfile
from pathlib import Path


DOCKER_IMAGE = "python:3.13-slim"


def test_in_docker(code: str, test_data: dict) -> tuple[bool, dict | str]:
    """Run generated code in a short-lived container and return (success, result/error)."""
    docker = shutil.which("docker")
    if not docker:
        return False, "Docker was not found on PATH. Install Docker Desktop to run the sandbox."

    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        (folder / "generated.py").write_text(code, encoding="utf-8")
        (folder / "input.json").write_text(json.dumps(test_data), encoding="utf-8")
        command = [
            docker, "run", "--rm", "--network", "none", "--read-only",
            "--tmpfs", "/tmp", "--memory", "128m", "--cpus", "0.5",
            "-v", f"{folder}:/work:ro", DOCKER_IMAGE,
            "python", "-c",
            ("import json, sys; sys.path.insert(0, '/work'); "
             "from generated import extract; "
             "result = extract(json.load(open('/work/input.json'))); "
             "assert set(result) == {'name', 'age', 'city'}; "
             "print(json.dumps(result))"),
        ]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            return False, "Sandbox timed out"

        if completed.returncode != 0:
            return False, completed.stderr.strip() or completed.stdout.strip()
        try:
            return True, json.loads(completed.stdout.strip())
        except json.JSONDecodeError:
            return False, "Sandbox returned invalid JSON: " + completed.stdout
