import json
import os
import re
from agents.analyzer import _ask_llm


def _fallback_code(mapping: dict) -> str:
    paths = {key: mapping[key].split(".") for key in ("name", "age", "city")}
    return f'''def extract(data):
    return {{
        "name": data[{paths["name"][0]!r}][{paths["name"][1]!r}],
        "age": data[{paths["age"][0]!r}][{paths["age"][1]!r}][{paths["age"][2]!r}],
        "city": data[{paths["city"][0]!r}][{paths["city"][1]!r}][{paths["city"][2]!r}],
    }}
'''


def _clean_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def generate(new_response: dict, mapping: dict, previous_memory: dict | None = None,
             intentionally_invalid: bool = False) -> str:
    if intentionally_invalid:
        return "def extract(data):\n    return data[\"missing\"]"

    prompt = f"""Generate ONLY Python code with def extract(data) for this mapping.
The function must return exactly the keys name, age, city.
New response: {json.dumps(new_response)}
Mapping: {json.dumps(mapping)}
Previous attempt information: {json.dumps(previous_memory or {})}"""
    llm_text = _ask_llm(prompt)
    if llm_text:
        return _clean_code(llm_text)

    print("[CODER] No LLM_API_KEY; using simple local code generation fallback")
    return _fallback_code(mapping)
