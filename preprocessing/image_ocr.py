
import pytesseract  # Tesseract OCR engine ko Python se use karne ke liye.

from PIL import Image  # Image open karne ke liye.

from pathlib import Path  # Image file path handle karne ke liye.
# Tesseract OCR software ka Windows path set kar rahe hain.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_image_text(image_path):  # Image se text extract karne ka function.

    image_path = Path(image_path)  # Image path ko Path object mein convert kar rahe hain.

    if not image_path.exists():  # Check kar rahe hain ki image available hai ya nahi.
        raise FileNotFoundError(f"Image not found: {image_path}")  # Missing image par error denge.

    with Image.open(image_path) as image:  # Image ko open kar rahe hain.

        extracted_text = pytesseract.image_to_string(image)  # OCR se image ka readable text extract kar rahe hain.

    return extracted_text.strip()  # Extra spaces remove karke text return kar rahe hain.
