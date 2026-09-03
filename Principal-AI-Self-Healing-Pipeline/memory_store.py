import json
from json import JSONDecodeError
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory" / "memory.json"


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {}

    raw_memory = MEMORY_FILE.read_text(encoding="utf-8").strip()
    if not raw_memory:
        return {}

    try:
        loaded_memory = json.loads(raw_memory)
    except JSONDecodeError:
        return {}

    return loaded_memory if isinstance(loaded_memory, dict) else {}


def save_attempt(code: str, mapping: dict, success: bool, error: str | None = None) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps({
        "last_attempt": {"code": code, "mapping": mapping, "success": success, "error": error}
    }, indent=2), encoding="utf-8")
