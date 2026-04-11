# main_pipeline.py
import sqlite3
import json
from deepseek_test_split import classify_text
from receipt_json_split import insert_receipt
from test_ocr_split import extract_text

DB_NAME = "expenses.db"

def setup_database():
    """Create SQLite database and receipts table if not exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        item_name TEXT,
        unit_price REAL,
        quantity REAL,
        total_paid REAL,
        payment_mode TEXT
    )
    """)
    conn.commit()
    conn.close()

def clean_json_string(json_str):
    """Remove unwanted characters like code fences, spaces, or newlines."""
    json_str = json_str.strip()  # Remove leading/trailing whitespace
    if json_str.startswith("```json"):
        json_str = json_str[7:]  # Remove starting ```json
    if json_str.startswith("```"):
        json_str = json_str[3:]  # Remove starting ```
    if json_str.endswith("```"):
        json_str = json_str[:-3]  # Remove ending ```
    return json_str.strip()

def insert_receipt1(receipt_data):
    """Insert receipt data into SQLite database."""

    if not receipt_data:
        print("Error: Empty data received.")
        return

    # If it's a string, try to parse, else assume dict
    if isinstance(receipt_data, str):
        receipt_data = clean_json_string(receipt_data)
        try:
            receipt_json = json.loads(receipt_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
    else:
        receipt_json = receipt_data  # Already a dict

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for item in receipt_json.get("items", []):
        cursor.execute("""
            INSERT INTO receipts (date, category, item_name, unit_price, quantity, total_paid, payment_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            receipt_json.get("date"),
            receipt_json.get("category"),
            item.get("name"),
            item.get("unit_price"),
            item.get("qty"),
            item.get("amount"),
            receipt_json.get("payment_method")
        ))
    conn.commit()
    conn.close()
    print("Receipt data inserted successfully!")


def main_pipeline(image_path):
    """Full pipeline: OCR → DeepSeek → JSON → SQLite insert."""
    setup_database()  # Ensure database exists

    # Step 1: OCR processing
    ocr_text = extract_text(image_path)
    print(f"OCR Text Extracted:\n{ocr_text}\n")

    # Step 2: DeepSeek call for structured extraction
    deepseek_output = classify_text(ocr_text)
    print(f"DeepSeek Output:\n{deepseek_output}\n")
    

    # Step 3: Extract final JSON
    # receipt_json_str = insert_receipt(deepseek_output)
    receipt_json_str = deepseek_output  # directly use DeepSeek's output
    
    print(f"Final Receipt JSON:\n{receipt_json_str}\n")

    # Step 4: Insert into SQLite
    insert_receipt1(receipt_json_str)

if __name__ == "__main__":
    image_path = r"C:\Users\agosw\Downloads\how-to-make-food-receipts-online-by-customizing-templates.png"  # Change to your receipt image
    main_pipeline(image_path)
