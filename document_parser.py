import os

from PyPDF2 import PdfReader
from docx import Document


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_path)
    elif ext in (".txt", ".md"):
        return _extract_plain(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，请上传 PDF、DOCX 或 TXT 文件。")


def _extract_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_plain(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
