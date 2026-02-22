import pytesseract
from PIL import Image
import os

def extract_text_from_certificate(file_path):
    """
    Extract raw text from a certificate file.
    Supports: PNG, JPG, JPEG.
    """
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()

        return ""
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
