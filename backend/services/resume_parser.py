import io
from typing import Dict
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

def text_from_pdf_bytes(b: bytes) -> str:
    try:
        text = pdf_extract_text(io.BytesIO(b))
        if text and len(text.strip())>10:
            return text
    except Exception:
        pass
    # fallback to OCR
    try:
        pages = convert_from_bytes(b)
        text = ""
        for p in pages:
            text += pytesseract.image_to_string(p)
        return text
    except Exception:
        return ""

def text_from_docx_bytes(b: bytes) -> str:
    f = io.BytesIO(b)
    doc = Document(f)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def parse_resume_file(content: bytes, filename: str) -> Dict:
    filename = filename.lower()
    text = ""
    if filename.endswith(".pdf"):
        text = text_from_pdf_bytes(content)
    elif filename.endswith(".docx"):
        text = text_from_docx_bytes(content)
    else:
        # try generic
        text = content.decode(errors="ignore")
    # very simple metadata extraction (name heuristics)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else "unknown"
    return {"filename": filename, "text": text, "name": name}
