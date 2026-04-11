# insert_receipt.py
import sqlite3
import json

# Example: your DeepSeek JSON (replace this with your actual JSON variable)
receipt_json = json.loads(receipt_json_temp)

# 1. Connect to SQLite
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# 2. Loop through items and insert each as a row
for item in receipt_json["items"]:
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

# 3. Commit and close connection
conn.commit()
conn.close()

print("Receipt data inserted successfully!")
