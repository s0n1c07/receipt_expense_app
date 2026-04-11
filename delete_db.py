import sqlite3

DB_NAME = "expenses.db"  # Replace with your DB name

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("DELETE FROM receipts")  # Clear all rows from receipts table
conn.commit()
conn.close()

print("All data cleared from receipts table.")
