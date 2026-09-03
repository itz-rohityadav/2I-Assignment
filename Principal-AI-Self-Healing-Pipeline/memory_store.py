import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory" / "memory.json"


def load_memory() -> dict:
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))


def save_attempt(code: str, mapping: dict, success: bool, error: str | None = None) -> None:
    MEMORY_FILE.write_text(json.dumps({
        "last_attempt": {"code": code, "mapping": mapping, "success": success, "error": error}
    }, indent=2), encoding="utf-8")
