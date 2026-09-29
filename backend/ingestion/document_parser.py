import os
from typing import List, Dict, Any, Tuple
import pymupdf as fitz
import docx

from backend.ai.ocr_engine import get_ocr_engine

class DocumentParser:
    """
    Parses PDF, DOCX, TXT, MD, and image files locally.
    Never transmits file content to remote servers.
    """
    @staticmethod
    def parse_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Parses PDF file page-by-page.
        Returns: (pages_list, total_page_count)
        """
        pages = []
        doc = fitz.open(file_path)
        total_pages = len(doc)

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_text = page.get_text("text").strip()
            
            # If page text is very sparse (scanned PDF page), try to extract text from drawings/annotations
            if not page_text:
                blocks = page.get_text("blocks")
                block_texts = [b[4].strip() for b in blocks if len(b) > 4 and b[4].strip()]
                page_text = "\n".join(block_texts)

            pages.append({
                "page_number": page_idx + 1,
                "text": page_text,
                "char_count": len(page_text)
            })

        doc.close()
        return pages, total_pages

    @staticmethod
    def parse_docx(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Parses DOCX document paragraphs and tables into structured sections.
        """
        doc = docx.Document(file_path)
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)

        # Include table contents
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)

        full_text = "\n\n".join(paragraphs)
        # Approximate 1 page per 3000 characters
        pages = [{"page_number": 1, "text": full_text, "char_count": len(full_text)}]
        return pages, 1

    @staticmethod
    def parse_txt(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """Parses plain text and Markdown files."""
        encodings = ["utf-8", "latin-1", "cp1252"]
        content = ""
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, OSError):
                continue

        pages = [{"page_number": 1, "text": content.strip(), "char_count": len(content)}]
        return pages, 1

    @staticmethod
    def parse_image(file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """Runs local OCR and visual layout extraction on image."""
        ocr = get_ocr_engine()
        result = ocr.analyze_image(file_path)
        text_content = result.get("text", "")
        
        pages = [{
            "page_number": 1,
            "text": text_content,
            "char_count": len(text_content),
            "metadata": result
        }]
        return pages, 1

    @classmethod
    def parse(cls, file_path: str, filename: str) -> Tuple[List[Dict[str, Any]], int, str]:
        """
        Auto-detects format and parses.
        Returns: (pages, page_count, detected_type)
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            pages, count = cls.parse_pdf(file_path)
            return pages, count, "pdf"
        elif ext == ".docx":
            pages, count = cls.parse_docx(file_path)
            return pages, count, "docx"
        elif ext in [".txt", ".md"]:
            pages, count = cls.parse_txt(file_path)
            return pages, count, "text"
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            pages, count = cls.parse_image(file_path)
            return pages, count, "image"
        else:
            raise ValueError(f"Unsupported format: {ext}")
