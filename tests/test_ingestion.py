import os
import pytest
from backend.ingestion.document_parser import DocumentParser

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")

def test_parse_pdf():
    pdf_path = os.path.join(SAMPLE_DIR, "qualcomm_snapdragon_whitepaper.pdf")
    assert os.path.exists(pdf_path), "Sample PDF should exist"
    pages, count, doc_type = DocumentParser.parse(pdf_path, "qualcomm_snapdragon_whitepaper.pdf")
    assert doc_type == "pdf"
    assert count == 4
    assert len(pages) == 4
    assert "Snapdragon" in pages[0]["text"]
    assert "TOPS" in pages[0]["text"]

def test_parse_docx():
    docx_path = os.path.join(SAMPLE_DIR, "quarterly_ai_strategy.docx")
    assert os.path.exists(docx_path), "Sample DOCX should exist"
    pages, count, doc_type = DocumentParser.parse(docx_path, "quarterly_ai_strategy.docx")
    assert doc_type == "docx"
    assert count == 1
    assert "Strategy" in pages[0]["text"]
    assert "Action Item" in pages[0]["text"]

def test_parse_txt():
    txt_path = os.path.join(SAMPLE_DIR, "developer_system_log.txt")
    assert os.path.exists(txt_path), "Sample TXT should exist"
    pages, count, doc_type = DocumentParser.parse(txt_path, "developer_system_log.txt")
    assert doc_type == "text"
    assert "SnapAssist" in pages[0]["text"]
    assert "QNNExecutionProvider" in pages[0]["text"]

def test_parse_image():
    img_path = os.path.join(SAMPLE_DIR, "system_architecture_screenshot.png")
    assert os.path.exists(img_path), "Sample image should exist"
    pages, count, doc_type = DocumentParser.parse(img_path, "system_architecture_screenshot.png")
    assert doc_type == "image"
    assert len(pages) == 1
    assert "metadata" in pages[0]
    assert pages[0]["metadata"]["dimensions"]["width"] == 900
