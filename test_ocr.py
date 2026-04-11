import pytesseract
from PIL import Image

# Path to your receipt image
image_path = r"C:\Users\agosw\Downloads\how-to-make-food-receipts-online-by-customizing-templates.png"

# Run OCR
text = pytesseract.image_to_string(Image.open(image_path))

print("Extracted Text:")
print(text)
