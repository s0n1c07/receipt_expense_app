# insert_receipt.py
import sqlite3
import json
import re

def clean_json_string(receipt_json_str):
    # Remove ```json and ``` wrappers
    cleaned_str = re.sub(r"```[a-zA-Z]*\n?", "", receipt_json_str)
    cleaned_str = cleaned_str.strip().rstrip("`")
    return cleaned_str


def insert_receipt(receipt_json_str):
    """
    Inserts receipt data into the SQLite database.
    
    Args:
        receipt_json_str (str): JSON string containing receipt data.
    """
    receipt_json_str = clean_json_string(receipt_json_str)

    # Parse JSON
    receipt_json = json.loads(receipt_json_str)

    # Connect to SQLite
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    # Loop through items and insert each as a row
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

    # Commit and close connection
    conn.commit()
    conn.close()

    print("Receipt data inserted successfully!")
