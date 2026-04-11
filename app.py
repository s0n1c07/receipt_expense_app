# app.py
import sqlite3
import requests
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session

from werkzeug.utils import secure_filename
# from deepseek_test_split import classify_text
# from receipt_json_split import insert_receipt
from test_ocr_split import extract_text
import re

def clean_ocr_text(text):
    # Remove non-ASCII characters
    text = text.encode("ascii", errors="ignore").decode()
    # Remove random symbols
    text = re.sub(r"[^a-zA-Z0-9\s\.\,\-\:]", "", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()

app = Flask(__name__)
app.secret_key = "dev-secret"  # replace later
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTS = {"png", "jpg", "jpeg", "webp"}
DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
print("DB Path:", DB_PATH)
print("Exists?", os.path.exists(DB_PATH))

@app.route("/dashboard")
def dashboard():
    import sqlite3

    # Connect to your database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all rows
    cursor.execute("SELECT * FROM receipts")
    rows = cursor.fetchall()

    # Fetch column names
    columns = [description[0] for description in cursor.description]

    conn.close()

    return render_template("dashboard.html", columns=columns, rows=rows)


def get_all_receipts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def run_query(sql_query):
    '''conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    conn.close()
    return rows'''
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    rows = cursor.fetchall()
    colnames = [d[0] for d in cursor.description] if cursor.description else None
    conn.close()
    return rows, colnames

DEEPSEEK_API_KEY = "sk-9b37a40b3f2e4653adfecb6434aa76e7"  # Replace with real key
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
url="https://api.deepseek.com/v1/chat/completions"
MODEL="deepseek-chat"
'''
def generate_sql(user_msg):
    prompt = f"""
    You are an SQL expert. Given the following question, write a SQL query
    to retrieve data from a table called 'expenses'.

    Question: {user_msg}
    SQL:
    """
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(DEEPSEEK_URL, headers=headers, data=json.dumps(data))
    sql = response.json()["choices"][0]["message"]["content"].strip()
    return sql
'''
def classify_text(ocr_text):
    """
    Parse receipt text using DeepSeek API and return structured JSON.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    # Debug log for OCR input
    print(f"[DEBUG] OCR_TEXT:\n{ocr_text}\n")

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

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"[DEBUG] Raw API Response: {resp.text}")

        j = resp.json()
        if "choices" in j and len(j["choices"]) > 0:
            msg = j["choices"][0].get("message", {}).get("content")
            print(f"[DEBUG] DeepSeek Returned Message:\n{msg}")

            if msg:
                try:
                    receipt_json = json.loads(msg)
                except json.JSONDecodeError:
                    match = re.search(r"\{.*\}", msg, re.S)
                    receipt_json = json.loads(match.group()) if match else None
                return receipt_json
        return None

    except Exception as e:
        print("[ERROR] Could not parse DeepSeek response:", e)
        print("[DEBUG] Full Response Text:\n", resp.text)
        return None


def insert_receipt(receipt_json):
    """
    Inserts receipt data into the SQLite database.
    
    Args:
        receipt_json (dict): Dictionary containing receipt data.
    """

    # Validate type
    if not isinstance(receipt_json, dict):
        raise ValueError("insert_receipt expects a dictionary, got: " + str(type(receipt_json)))

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

def generate_sql(user_msg):
    prompt = f"""
    You are an SQL expert. Given the following question, write a SQL query
    to retrieve data from a table called 'receipts' and columns names are
    data, category, item_name, unit_price, quantity, total_paid, payment_mode.

    Only output raw SQL without explanations or code fences.

    Question: {user_msg}
    SQL:
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(DEEPSEEK_URL, headers=headers, data=json.dumps(data))
    sql = response.json()["choices"][0]["message"]["content"].strip()

    # Remove possible ```sql ... ``` wrappers
    if sql.startswith("```"):
        sql = sql.strip("`")
        sql = sql.replace("sql", "", 1).strip()
    return sql



def allowed_file(fname: str) -> bool:
    return "." in fname and fname.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@app.route("/")
def home():
    return render_template("upload.html")

'''@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("receipt_image")
    if not file or file.filename == "":
        return "No file selected", 400
    if not allowed_file(file.filename):
        return "Unsupported file type", 400

    fname = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, fname)
    file.save(save_path)

    # TODO: next steps will OCR -> DeepSeek -> insert into SQLite here
    print(f"Saved: {save_path}")

    return redirect(url_for("chat"))
'''

''' latest commented @app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("receipt_image")
    if not file or file.filename == "":
        return "No file selected", 400
    if not allowed_file(file.filename):
        return "Unsupported file type", 400

    fname = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, fname)
    file.save(save_path)
    print(f"Saved: {save_path}")

    try:
        print(f"[DEBUG] Running OCR on: {save_path}")
        ocr_text = extract_text(save_path)
        ocr_text = clean_ocr_text(ocr_text)

        print(f"[DEBUG] OCR Output: {ocr_text}")

        if not ocr_text.strip():
            raise ValueError("OCR returned empty text")

        print("[DEBUG] Sending text to DeepSeek...")
        receipt_json = classify_text(ocr_text)
        print(f"[DEBUG] DeepSeek Output: {receipt_json}")



        if not isinstance(receipt_json, dict):
            raise ValueError("DeepSeek classification returned invalid format")

        print("[DEBUG] Inserting into database...")
        insert_receipt(receipt_json)
        print("Receipt processed and saved to database successfully!")


    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        return f"Processing error: {e}", 500


    # Redirect to chat after processing
    return redirect(url_for("chat"))'''


def process_receipt(save_path):
    try:
        print(f"[DEBUG] Running OCR on: {save_path}")
        ocr_text = extract_text(save_path)
        ocr_text = clean_ocr_text(ocr_text)

        print(f"[DEBUG] OCR Output: {ocr_text}")

        if not ocr_text.strip():
            raise ValueError("OCR returned empty text")

        print("[DEBUG] Sending text to DeepSeek...")
        receipt_json = classify_text(ocr_text)
        print(f"[DEBUG] DeepSeek Output: {receipt_json}")

        if not isinstance(receipt_json, dict):
            raise ValueError("DeepSeek classification returned invalid format")

        print("[DEBUG] Inserting into database...")
        insert_receipt(receipt_json)
        print("Receipt processed and saved to database successfully!")

    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        raise


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("receipt_image")
    if not file or file.filename == "":
        return "No file selected", 400
    if not allowed_file(file.filename):
        return "Unsupported file type", 400

    fname = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, fname)
    file.save(save_path)
    print(f"Saved: {save_path}")

    try:
        process_receipt(save_path)
    except Exception as e:
        return f"Processing error: {e}", 500

    return redirect(url_for("chat"))





'''@app.route("/chat", methods=["GET", "POST"])
    def chat():
        response = None
        if request.method == "POST":
            user_msg = request.form.get("message", "")
            # TODO: next step will run NL->SQL on expenses.db
            response = f"(stub) You said: {user_msg}"
        return render_template("chat.html", response=response)'''
'''    
@app.route("/chat", methods=["GET", "POST"])
def chat():
    response = None
    if request.method == "POST":
        user_msg = request.form.get("message", "")
        try:
            sql_query = generate_sql(user_msg)
            rows = run_query(sql_query)
            response = f"SQL: {sql_query}\n\nResults: {rows}"
        except Exception as e:
            response = f"Error: {str(e)}"
    return render_template("chat.html", response=response)
'''
def clean_sql(sql):
    # Remove triple backticks and "sql" language tag
    sql = sql.replace("```sql", "").replace("```", "")
    return sql.strip().rstrip(";")


def validate_sql(sql):
    forbidden = ["DROP", "DELETE", "UPDATE", ";"]
    return not any(word in sql.upper() for word in forbidden)

'''
@app.route("/chat", methods=["GET", "POST"])
def chat():
    response = None
    if request.method == "POST":
        user_msg = request.form.get("message", "")
        try:
            # 1. Generate SQL
            sql_query = generate_sql(user_msg)
            sql_query = clean_sql(sql_query)
            print("Generated SQL:", sql_query)  # Debug

            # 2. Validate SQL before running
            if not validate_sql(sql_query):
                response = "Unsafe query detected."
            else:
                rows = run_query(sql_query)

                # 3. Build DeepSeek prompt
                prompt = f"""
                The user asked: "{user_msg}"

                SQL query used:
                {sql_query}

                Raw database results:
                {rows}

                Please explain breifly the result in natural, paragraph-style text.
                """

                # 4. Send to DeepSeek API
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant for finance data."},
                        {"role": "user", "content": prompt}
                    ]
                }
                r = requests.post(DEEPSEEK_URL, headers=headers, json=data)
                r.raise_for_status()
                completion = r.json()

                # 5. Extract model reply
                response = completion["choices"][0]["message"]["content"].strip()

        except sqlite3.Error as db_err:
            response = f"Database Error: {db_err}"
        except Exception as e:
            response = f"Error: {e}"

    return render_template("chat.html", response=response)'''


def process_query(user_msg, chat_history=None):
    """Process a user query and return assistant reply."""
    if chat_history is None:
        chat_history = []

    # 1. Generate SQL
    sql_query = generate_sql(user_msg)
    sql_query = clean_sql(sql_query)

    if not validate_sql(sql_query):
        return "Unsafe query detected."

    rows = run_query(sql_query)

    # 2. Build DeepSeek prompt
    prompt = f"""
    The user asked: "{user_msg}"
    SQL query used:
    {sql_query}
    Raw database results:
    {rows}
    Please explain briefly the result in natural, paragraph-style text.
    """

    # 3. Prepare conversation history for API
    messages = [{"role": "system", "content": "You are helpful assistant for finance data."}]
    for entry in chat_history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})
    messages.append({"role": "user", "content": prompt})

    # 4. Send to DeepSeek
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    data = {"model": MODEL, "messages": messages}
    r = requests.post(DEEPSEEK_URL, headers=headers, json=data)
    r.raise_for_status()
    completion = r.json()

    assistant_reply = completion["choices"][0]["message"]["content"].strip()
    return assistant_reply

'''above one is new func'''

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "chat_history" not in session:
        session["chat_history"] = []  # initialize history

    '''if request.method == "POST":
        user_msg = request.form.get("message", "")

        try:
            # 1. Generate SQL
            sql_query = generate_sql(user_msg)
            sql_query = clean_sql(sql_query)
            print("Generated SQL:", sql_query)  # Debug

            # 2. Validate SQL
            if not validate_sql(sql_query):
                assistant_reply = "Unsafe query detected."
            else:
                rows = run_query(sql_query)

                # 3. Build DeepSeek prompt
                prompt = f"""
                The user asked: "{user_msg}"

                SQL query used:
                {sql_query}

                Raw database results:
                {rows}

                Please explain briefly the result in natural, paragraph-style text.
                """

                # 4. Prepare conversation history for API
                messages = [{"role": "system", "content": "You are a helpful assistant for finance data."}]
                for entry in session["chat_history"]:
                    messages.append({"role": "user", "content": entry["user"]})
                    messages.append({"role": "assistant", "content": entry["assistant"]})
                messages.append({"role": "user", "content": prompt})

                # 5. Send to DeepSeek
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {"model": MODEL, "messages": messages}
                r = requests.post(DEEPSEEK_URL, headers=headers, json=data)
                r.raise_for_status()
                completion = r.json()

                assistant_reply = completion["choices"][0]["message"]["content"].strip()

            # 6. Save to session chat history
            session["chat_history"].append({"user": user_msg, "assistant": assistant_reply})
            session.modified = True  # mark session as updated

        except sqlite3.Error as db_err:
            assistant_reply = f"Database Error: {db_err}"
        except Exception as e:
            assistant_reply = f"Error: {e}" undo this one if bt'''
    if request.method == "POST":
        user_msg = request.form.get("message", "")
        try:
            assistant_reply = process_query(user_msg, session["chat_history"])
            # Save to session history
            session["chat_history"].append({"user": user_msg, "assistant": assistant_reply})
            session.modified = True
        except sqlite3.Error as db_err:
            assistant_reply = f"Database Error: {db_err}"
        except Exception as e:
            assistant_reply = f"Error: {e}"
    '''this is new one'''
    
    return render_template("chat.html", chat_history=session["chat_history"])

@app.route("/chatbot", methods=["POST"])
def chatbot_api():
    data = request.get_json()
    user_msg = data.get("query", "")
    assistant_reply = process_query(user_msg)  # no session needed
    return {"answer": assistant_reply}


def ensure_history():
    if "chat_history" not in session:
        session["chat_history"] = []
    return session["chat_history"]

def add_msg(role, content):
    hist = ensure_history()
    hist.append({"role": role, "content": content})
    session["chat_history"] = hist  # reassign to mark session dirty

def get_history():
    return session.get("chat_history", [])

def rows_to_markdown(rows, colnames=None):
    # rows: list of tuples; colnames: optional list of column names
    if rows is None:
        return "No rows."
    if not rows:
        return "No results."
    # If no column names given, make generic
    if not colnames:
        colnames = [f"col{i+1}" for i in range(len(rows[0]))]
    # Build a simple markdown table
    header = "| " + " | ".join(colnames) + " |"
    sep = "|" + "|".join([" --- "]*len(colnames)) + "|"
    body = "\n".join(["| " + " | ".join([str(x) for x in r]) + " |" for r in rows])
    return "\n".join([header, sep, body])


if __name__ == "__main__":
    app.run(debug=True)
