# deepseek_test.py
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()  # loads .env file

'''API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE = os.getenv("DEEPSEEK_API_BASE")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")'''

API_KEY = "sk-9b37a40b3f2e4653adfecb6434aa76e7"
BASE = os.getenv("DEEPSEEK_API_BASE").strip()
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
url="https://api.deepseek.com/v1/chat/completions"
if not API_KEY or not BASE:
    raise SystemExit("Please set DEEPSEEK_API_KEY and DEEPSEEK_API_BASE in your .env file")
'''
def classify_text(ocr_text):
    """
    Send OCR text to DeepSeek API and return structured JSON.
    :param ocr_text: string extracted from receipt image
    :return: Python dict of parsed receipt
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # Build prompt for structured JSON
    prompt = f"""
    You are a reliable assistant. Parse the following RECEIPT TEXT and return ONLY valid JSON.
    OCR_TEXT:
    \"\"\"{ocr_text}\"\"\"

    Return JSON with these fields:
    - date: YYYY-MM-DD or null
    - merchant: string or null
    - category: one of [essentials, entertainment, medical, fuel, food, other]
    give always in all small caps
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

    resp = requests.post(url, headers=headers, json=payload, timeout=30)

    try:
        j = resp.json()
        if "choices" in j and len(j["choices"]) > 0:
            # Get content from the first choice
            msg = j["choices"][0].get("message", {}).get("content")
            if msg:
                try:
                    # Try direct JSON parsing
                    receipt_json = json.loads(msg)
                except json.JSONDecodeError:
                    # Extract JSON substring using regex
                    import re
                    match = re.search(r"\{.*\}", msg, re.S)
                    receipt_json = json.loads(match.group()) if match else None
                return receipt_json
            else:
                return None
        else:
            return None
    except Exception as e:
        print("Could not parse JSON response:", e)
        print("Full response text:\n", resp.text)
        return None
'''


def classify_text(ocr_text):
    """
    Send OCR text to DeepSeek API and return structured JSON.
    :param ocr_text: string extracted from receipt image
    :return: Python dict of parsed receipt
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""
    You are a reliable assistant. Parse the following RECEIPT TEXT and return ONLY valid JSON.
    OCR_TEXT:
    \"\"\"{ocr_text}\"\"\"

    Return JSON with these fields:
    - date: YYYY-MM-DD or null
    - merchant: string or null
    - category: one of [essentials, entertainment, medical, fuel, food, other]
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

    print("[DEBUG] Sending payload to DeepSeek API...")
    print("[DEBUG] Payload Prompt:\n", prompt)

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        print("[DEBUG] Raw API Response:", resp.text)
    except requests.exceptions.RequestException as e:
        print("[ERROR] Request failed:", e)
        return None

    try:
        j = resp.json()
        if "choices" in j and len(j["choices"]) > 0:
            msg = j["choices"][0].get("message", {}).get("content")
            print("[DEBUG] DeepSeek Returned Content:\n", msg)
            if msg:
                try:
                    return json.loads(msg)
                except json.JSONDecodeError:
                    import re
                    match = re.search(r"\{.*\}", msg, re.S)
                    if match:
                        try:
                            return json.loads(match.group())
                        except json.JSONDecodeError as e:
                            print("[ERROR] Regex JSON parse failed:", e)
                            return None
                    else:
                        print("[ERROR] No JSON found in response.")
                        return None
            else:
                print("[ERROR] No message content in DeepSeek response.")
                return None
        else:
            print("[ERROR] No choices in DeepSeek response.")
            return None
    except Exception as e:
        print("[ERROR] Could not parse JSON response:", e)
        print("[DEBUG] Full response text:\n", resp.text)
        return None


if __name__ == "__main__":
    test_text = "4 Cheese Burger 5.99 23.96 4 Soda 0.49 1.96 Sales Tax 1.28 VISA 32.10"
    result = classify_text(test_text)

    if result is None:
        print("DeepSeek returned no structured data.")
    else:
        print("Structured JSON from DeepSeek:\n", json.dumps(result, indent=2))
