# deepseek_test.py
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # loads .env file

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE = os.getenv("DEEPSEEK_API_BASE")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not API_KEY or not BASE:
    raise SystemExit("Please set DEEPSEEK_API_KEY and DEEPSEEK_API_BASE in your .env file")

url = BASE.rstrip("/") + "/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# --- Load OCR text dynamically ---
ocr_file = Path("ocr_output.txt")
if not ocr_file.exists():
    raise FileNotFoundError("ocr_output.txt not found in project folder")
ocr_text = ocr_file.read_text(encoding="utf-8")

# Build prompt for structured JSON
prompt = f"""
You are a reliable assistant. Parse the following RECEIPT TEXT and return ONLY valid JSON.
OCR_TEXT:
\"\"\"{ocr_text}\"\"\"

Return JSON with these fields:
- date: YYYY-MM-DD or null
- merchant: string or null
- category: one of [Essentials, Entertainment, Medical, Fuel, Food, Other]
- total_amount: float or null
- currency: currency symbol or code if present
- items: array of objects [{{
    name: string,
    qty: number or null,
    unit_price: number or null,
    amount: number or null
}}]
- payment_method: CASH, VISA, MASTER, null
"""

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 600,
    "temperature": 0.0
}

print("Calling DeepSeek endpoint:", url)
resp = requests.post(url, headers=headers, json=payload, timeout=30)

print("HTTP status:", resp.status_code)
print("Raw response (first 1000 chars):")
print(resp.text[:1000])

# try to extract model content
try:
    j = resp.json()
    content = None
    if "choices" in j and len(j["choices"]) > 0:
        msg = j["choices"][0].get("message") or j["choices"][0].get("text")
        receipt_json_temp = json.loads(msg)
        if isinstance(msg, dict):
            content = msg.get("content")
        else:
            content = msg
    print("\nStructured JSON from DeepSeek:\n", content)
except Exception as e:
    print("\nCould not parse JSON response:", e)
    print("Full response text:\n", resp.text)
