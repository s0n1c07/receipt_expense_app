import gradio as gr
from deepseek_test_split import classify_text
from receipt_json_split import insert_receipt
from test_ocr_split import extract_text
'''from test_ocr_split import extract_text
from deepseek_test_split import classify_text
from receipt_json_split import insert_receipt1'''

def process_receipt(image):
    """
    Upload a receipt image, extract text, classify with DeepSeek,
    and store into SQLite database.
    """
    if image is None:
        return "No file uploaded."

    # 1. OCR
    ocr_text = extract_text(image.name)  # image.name works in Gradio file input

    # 2. DeepSeek call
    deepseek_json = classify_text(ocr_text)  # returns dict

    if deepseek_json is None:
        return "DeepSeek failed to process receipt."

    # 3. Insert into SQLite
    insert_receipt(deepseek_json)

    return "Receipt processed and stored successfully!"

iface = gr.Interface(
    fn=process_receipt,
    inputs=gr.File(file_types=[".png", ".jpg", ".jpeg"]),
    outputs="text",
    title="Receipt Expense Tracker",
    description="Upload a receipt image, it will be processed and stored in the database."
)

iface.launch()
