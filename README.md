# ReceiptIQ — AI-Powered Expense Tracker

> Upload a receipt. Ask questions in plain English. Get answers.

ReceiptIQ is a full-stack expense tracking application that uses OCR and a large language model to automatically extract structured data from receipt images, store it in a local database, and answer natural-language queries about your spending.

---

## Features

- **Receipt OCR** — extracts text from JPG/PNG/WEBP receipt images using Tesseract
- **LLM-powered parsing** — sends OCR text to DeepSeek to extract date, merchant, category, items, and payment method as structured JSON
- **SQLite storage** — persists all line items locally, no cloud database required
- **Natural language chat** — ask spending questions in plain English; the app generates SQL, runs it, and explains the result in natural language
- **Multi-interface** — Flask web app, Telegram bot, and Gradio UI all share the same core pipeline
- **Expense dashboard** — tabular view of all stored receipts

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Web framework | Flask | Lightweight, minimal boilerplate |
| OCR | Tesseract + Pillow | Open-source, runs locally, no API cost |
| LLM (parsing + NL→SQL) | DeepSeek API (`deepseek-chat`) | Cost-effective, strong instruction following |
| Database | SQLite (`expenses.db`) | Zero-config, single-file, perfect for single-user apps |
| Frontend | Jinja2 + Tailwind CSS (CDN) | Fast prototyping, no build step |
| Telegram interface | `python-telegram-bot` | Mobile-first receipt capture |
| Demo UI | Gradio | Quick testing without the full web app |

---

## Project Structure

```
.
├── app.py                  # Flask app — all routes and core logic
├── test_ocr_split.py       # OCR module: extract_text(image_path)
├── deepseek_test_split.py  # LLM module: classify_text(ocr_text)
├── receipt_json_split.py   # DB module: insert_receipt(receipt_json)
├── main_pipeline.py        # Standalone CLI pipeline for testing
├── gradio_app.py           # Gradio interface
├── telegram_bot.py         # Telegram bot interface
├── setup_sqlite.py         # Creates expenses.db and receipts table
├── delete_db.py            # Utility: clears all rows from receipts table
├── templates/
│   ├── base.html           # Shared layout with navbar
│   ├── upload.html         # Receipt upload page
│   ├── chat.html           # Chat interface
│   └── dashboard.html      # Data table view
├── static/
│   └── images/             # Logo and background assets
├── uploads/                # Saved receipt images (gitignored)
├── expenses.db             # SQLite database (gitignored)
└── .env                    # API keys and config (gitignored)
```

---

## Database Schema

```sql
CREATE TABLE receipts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         TEXT,
    category     TEXT,    -- essentials | food | medical | fuel | entertainment | other
    item_name    TEXT,
    unit_price   REAL,
    quantity     REAL,
    total_paid   REAL,
    payment_mode TEXT     -- CASH | VISA | MASTER | null
);
```

One row per line item. Date, category, and payment mode are repeated across rows from the same receipt.

---

## Setup

### Prerequisites

- Python 3.9+
- Tesseract OCR installed on your system
  - **macOS**: `brew install tesseract`
  - **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
  - **Windows**: [download the installer](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

```bash
git clone https://github.com/your-username/receiptiq.git
cd receiptiq

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
TELEGRAM_TOKEN=your_telegram_bot_token   # optional
```

### Initialize the Database

```bash
python setup_sqlite.py
```

### Run the Web App

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Run the Telegram Bot (optional)

```bash
python telegram_bot.py
```

### Run the Gradio Demo (optional)

```bash
python gradio_app.py
```

---

## How It Works

### Receipt Upload Pipeline

```
Image file
    └─► Tesseract OCR          (test_ocr_split.py)
            └─► clean_ocr_text()
                    └─► DeepSeek classify_text()   → structured JSON
                                └─► insert_receipt()  → SQLite rows
```

### Chat Query Pipeline

```
User question (natural language)
    └─► DeepSeek generate_sql()    → raw SQL string
            └─► clean_sql() + validate_sql()
                    └─► SQLite run_query()          → rows + column names
                            └─► DeepSeek explain    → natural language reply
```

---

## Example Chat Queries

```
How much did I spend on food last month?
What was my most expensive single purchase?
Show me all VISA transactions.
Which category had the highest total spending?
How many receipts have I uploaded?
```

---

## Known Limitations

- OCR accuracy drops significantly on blurry, low-contrast, or handwritten receipts
- The flat schema repeats receipt-level fields (date, category, payment) per line item — not normalized
- SQL injection protection is rule-based (`validate_sql` blocks DROP/DELETE/UPDATE) — not AST-level
- Chat history is session-scoped and resets on server restart
- API key in `app.py` must be moved to `.env` before any shared deployment

---

## Requirements

```
flask
pytesseract
pillow
requests
python-dotenv
python-telegram-bot==13.x
gradio
werkzeug
```

---

## License

MIT
