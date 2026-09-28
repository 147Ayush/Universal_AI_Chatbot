# Temporary helper: prints Gemini model IDs your key can use for chat.
import httpx
from app.config.settings import get_settings

resp = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    headers={"x-goog-api-key": get_settings().gemini_api_key},
    params={"pageSize": 100},
    timeout=30,
)
resp.raise_for_status()

for m in resp.json().get("models", []):
    if "generateContent" in m.get("supportedGenerationMethods", []):
        print(m["name"].removeprefix("models/"))