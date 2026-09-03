import json
import os
import urllib.request


EXPECTED_MAPPING = {
    "name": "user.full_name",
    "age": "user.details.age",
    "city": "user.details.location",
}


def _ask_llm(prompt: str) -> str | None:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None

    try:
        model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        request = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


def analyze(old_response: dict, new_response: dict, error: str) -> dict:
    prompt = f"""Compare these API responses and return ONLY a JSON object mapping name, age, and city
        to dot-separated paths in the new response.
        Old: {json.dumps(old_response)}
        New: {json.dumps(new_response)}
        Extraction error: {error}"""
    llm_text = _ask_llm(prompt)
    if llm_text:
        return json.loads(llm_text)

    print("[ANALYZER] No LLM_API_KEY; using the simple local mapping fallback")
    return EXPECTED_MAPPING.copy()
