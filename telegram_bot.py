import os
import logging
import requests
from app import process_receipt 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL", "http://127.0.0.1:5000")

if not TOKEN:
    raise SystemExit("ERROR: TELEGRAM_TOKEN not set in .env")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("Welcome! Send an image or a text query.\nUse /database to view database info.")
'''
def handle_image(update, context):
    try:
        # Get highest-resolution photo
        photo = update.message.photo[-1]
        file = context.bot.getFile(photo.file_id)
        file_path = "temp.jpg"
        file.download(file_path)

        with open(file_path, 'rb') as f:
            resp = requests.post(f"{APP_URL}/upload", files={'file': f})
        try:
            update.message.reply_text(str(resp.json()))
        except Exception:
            update.message.reply_text(resp.text)
    except Exception as e:
        logger.error("Image handling error", exc_info=True)
        update.message.reply_text(f"Error: {e}")'''

def handle_image(update, context):
    update.message.reply_text("Image received. Processing...") # Debug log
    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    save_path = f"uploads/{file.file_id}.jpg"
    file.download(save_path)

    try:
        print("[DEBUG] File downloaded, calling process_receipt")
        result = process_receipt(save_path)
        print(f"[DEBUG] process_receipt result: {result}")
        update.message.reply_text("Receipt processed successfully!")
    except Exception as e:
        print(f"[ERROR] {e}")
        update.message.reply_text(f"Error: {e}")

def handle_text(update, context):
    query = update.message.text
    try:
        resp = requests.post(f"{APP_URL}/chatbot", json={"query": query})
        answer = resp.json().get("answer", "No answer returned.")
        update.message.reply_text(answer)
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def see_database(update, context):
    try:
        resp = requests.get(f"{APP_URL}/database")
        try:
            update.message.reply_text(str(resp.json()))
        except Exception:
            update.message.reply_text(resp.text)
    except Exception as e:
        logger.error("Database error", exc_info=True)
        update.message.reply_text(f"Error: {e}")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("database", see_database))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
