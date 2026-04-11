# setup_sqlite.py
import sqlite3

# 1. Connect to SQLite database (it will create expenses.db if it doesn't exist)
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# 2. Create the receipts table
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

# 3. Commit changes and close connection
conn.commit()
conn.close()

print("SQLite database and receipts table created successfully!")
