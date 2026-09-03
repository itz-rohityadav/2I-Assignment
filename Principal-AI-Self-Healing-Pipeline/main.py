import importlib
import json
import shutil
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from agents.analyzer import analyze
from agents.coder import generate
from memory_store import load_memory, save_attempt
from sandbox.runner import test_in_docker

API_URL = "http://127.0.0.1:8000/users"
ACTIVE_FILE = Path(__file__).parent / "extractor" / "active_extractor.py"
BASELINE_FILE = Path(__file__).parent / "extractor" / "extractor.py"

load_dotenv()


def fetch_user(version: int) -> dict:
    with urllib.request.urlopen(f"{API_URL}?version={version}", timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def load_active_extractor():
    module = importlib.import_module("extractor.active_extractor")
    return importlib.reload(module).extract


def reset_active_extractor() -> None:
    ACTIVE_FILE.write_text(BASELINE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    importlib.invalidate_caches()


def run_pipeline() -> None:
    print("=== Autonomous Self-Healing Data Pipeline ===")
    reset_active_extractor()
    print("[RESET] Active extractor restored to V1 baseline")

    v1 = fetch_user(1)
    print(f"[API] V1 response: {v1}")
    print(f"[PIPELINE] V1 output: {load_active_extractor()(v1)}")
    print("[MONITOR] Extraction successful")

    v2 = fetch_user(2)
    print(f"\n[API] V2 response: {v2}")
    try:
        load_active_extractor()(v2)
        print("[MONITOR] Extraction successful (unexpected)")
        return
    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"
        print(f"[MONITOR] Extraction failed - schema changed ({error_message})")

    mapping = analyze(v1, v2, error_message)
    print(f"[ANALYZER] Mapping discovered: {json.dumps(mapping)}")
    previous_memory = load_memory().get("last_attempt")

    print("[CODER] Testing an intentionally bad first attempt")
    bad_code = generate(v2, mapping, previous_memory, intentionally_invalid=True)
    bad_ok, bad_result = test_in_docker(bad_code, v2)
    save_attempt(bad_code, mapping, bad_ok, None if bad_ok else str(bad_result))
    print(f"[SANDBOX] Bad attempt rejected: {bad_result}")

    print("[CODER] Generating corrected extractor")
    good_code = generate(v2, mapping, load_memory().get("last_attempt"))
    good_ok, good_result = test_in_docker(good_code, v2)
    if not good_ok:
        print(f"[SANDBOX] Corrected extractor failed: {good_result}")
        save_attempt(good_code, mapping, False, str(good_result))
        return

    print(f"[SANDBOX] Corrected extractor passed: {good_result}")
    ACTIVE_FILE.write_text(good_code + "\n", encoding="utf-8")
    save_attempt(good_code, mapping, True)
    print("[DEPLOY] New extractor is now active")
    print(f"[PIPELINE] V2 output: {load_active_extractor()(v2)}")
    print("[MONITOR] Extraction successful after self-healing")


if __name__ == "__main__":
    if not shutil.which("docker"):
        print("[WARNING] Docker is not installed or not on PATH; sandbox tests will be rejected.")
    try:
        run_pipeline()
    except urllib.error.URLError:
        print("[ERROR] Start the mock API first: uvicorn mock_api.main:app --reload")
