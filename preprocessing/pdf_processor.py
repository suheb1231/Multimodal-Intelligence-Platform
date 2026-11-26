
import fitz  # PDF pages read karne ke liye.

import pytesseract  # Scanned pages se OCR text extract karne ke liye.

from PIL import Image  # PDF page image ko OCR ke liye handle karne ke liye.

from pathlib import Path  # File paths handle karne ke liye.

import io  # PDF page image ko memory mein read karne ke liye.
import shutil
import os 


tesseract_path = shutil.which("tesseract")

if not tesseract_path and os.name == "nt":
    windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(windows_path):
        tesseract_path = windows_path

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_pdf_pages(pdf_path, asset_id):  # PDF processing function.

    pdf_path = Path(pdf_path)  # PDF path convert kar rahe hain.

    if not pdf_path.exists():  # PDF file check kar rahe hain.
        raise FileNotFoundError(f"PDF not found: {pdf_path}")  # Missing file par error.

    pages_data = []  # Processed pages store karne ke liye list.

    with fitz.open(pdf_path) as pdf:  # PDF open kar rahe hain.

        for page_number, page in enumerate(pdf, start=1):  # Har page read kar rahe hain.

            text = page.get_text("text").strip()  # Normal PDF text extract kar rahe hain.

            extraction_method = "pymupdf"  # Default extraction method set kar rahe hain.

            if not text:  # Agar page mein selectable text nahi mila.

                pix = page.get_pixmap(dpi=200)  # PDF page ko image mein convert kar rahe hain.

                image = Image.open(io.BytesIO(pix.tobytes("png")))  # Image ko memory se open kar rahe hain.

                text = pytesseract.image_to_string(image).strip()  # OCR se scanned page ka text nikal rahe hain.

                extraction_method = "tesseract_ocr"  # OCR method record kar rahe hain.

            page_data = {  # Page ka structured metadata bana rahe hain.

                "asset_id": asset_id,  # Original PDF ki unique ID.

                "source_file": pdf_path.name,  # Original PDF filename.

                "modality": "pdf",  # Asset modality.

                "segment_id": f"{asset_id}-PAGE-{page_number}",  # Unique page segment ID.

                "page_number": page_number,  # Original page number.

                "text": text,  # Extracted page text.

                "has_text": bool(text),  # Text available hai ya nahi.

                "extraction_method": extraction_method  # Text kis method se nikla.

            }

            pages_data.append(page_data)  # Page data list mein add kar rahe hain.

    return pages_data  # Saare processed pages return kar rahe hain.
