# test_ocr.py
import pytesseract
from PIL import Image

def extract_text(image_path):
    """
    Extract text from a receipt image using OCR.
    :param image_path: path to the image file
    :return: extracted text as a string
    """
    text = pytesseract.image_to_string(Image.open(image_path))
    return text

# Optional: run as standalone for testing
if __name__ == "__main__":
    image_path = r"C:\Users\agosw\Downloads\how-to-make-food-receipts-online-by-customizing-templates.png"
    extracted_text = extract_text(image_path)
    print("Extracted Text:")
    print(extracted_text)
