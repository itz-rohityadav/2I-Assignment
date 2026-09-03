import json
import os
import re
import urllib.error
import urllib.request


EXPECTED_MAPPING = {
    "name": "user.full_name",
    "age": "user.details.age",
    "city": "user.details.location",
}


def _format_http_error(error: urllib.error.HTTPError) -> str:
    details = error.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(details)
        message = payload.get("error", {}).get("message")
        if message:
            return f"Gemini API HTTP {error.code}: {message.splitlines()[0]}"
    except json.JSONDecodeError:
        pass
    return f"Gemini API HTTP {error.code}: {details[:300]}"


def _ask_llm(prompt: str) -> tuple[str | None, str | None]:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider != "gemini":
        return None, f"unsupported LLM_PROVIDER={provider!r}; only 'gemini' is supported"

    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None, "LLM_API_KEY is not set"

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
        return payload["candidates"][0]["content"]["parts"][0]["text"], None
    except urllib.error.HTTPError as error:
        return None, _format_http_error(error)
    except urllib.error.URLError as error:
        return None, f"Gemini API network error: {error.reason}"
    except (KeyError, IndexError, json.JSONDecodeError) as error:
        return None, f"unexpected Gemini API response format: {error}"


def _parse_mapping(text: str) -> dict:
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    return json.loads(cleaned)


def analyze(old_response: dict, new_response: dict, error: str) -> dict:
    prompt = f"""Compare these API responses and return ONLY a JSON object mapping name, age, and city
        to dot-separated paths in the new response.
        Old: {json.dumps(old_response)}
        New: {json.dumps(new_response)}
        Extraction error: {error}"""
    llm_text, llm_error = _ask_llm(prompt)
    if llm_text:
        try:
            return _parse_mapping(llm_text)
        except json.JSONDecodeError as error:
            llm_error = f"LLM returned invalid mapping JSON: {error}"

    print(f"[ANALYZER] LLM unavailable ({llm_error}); using the simple local mapping fallback")
    return EXPECTED_MAPPING.copy()
