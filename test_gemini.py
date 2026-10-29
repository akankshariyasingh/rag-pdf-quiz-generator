
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY", "").strip()

if len(api_key) < 20:
    print("ERROR: GEMINI_API_KEY is missing or incomplete.")
    raise SystemExit(1)

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)

response = requests.post(
    url,
    headers={
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    },
    json={
        "contents": [
            {
                "parts": [
                    {"text": "Reply with exactly: Gemini is working"}
                ]
            }
        ]
    },
    timeout=30,
)

print("HTTP status:", response.status_code)

if response.ok:
    print("SUCCESS:", response.json())
else:
    print("ERROR:", response.text)
