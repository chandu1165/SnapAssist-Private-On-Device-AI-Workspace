import os
import re
import uuid
import shutil
from typing import Tuple

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".png", ".jpg", ".jpeg", ".webp"}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or malformed characters."""
    base = os.path.basename(filename)
    # Strip illegal characters for Windows and Unix
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
    if not clean_name:
        clean_name = f"doc_{uuid.uuid4().hex[:8]}"
    return clean_name

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def save_uploaded_file(original_filename: str, file_bytes: bytes) -> Tuple[str, str, str, int]:
    """
    Saves uploaded file safely.
    Returns: (doc_id, sanitized_filename, saved_file_path, file_size)
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    clean_name = sanitize_filename(original_filename)
    ext = os.path.splitext(clean_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    doc_id = str(uuid.uuid4())
    stored_name = f"{doc_id}_{clean_name}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    # Prevent symlink traversal out of UPLOAD_DIR
    real_target = os.path.abspath(file_path)
    real_upload_dir = os.path.abspath(UPLOAD_DIR)
    if not real_target.startswith(real_upload_dir):
        raise ValueError("Security violation: Target path escapes upload directory.")

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    file_size = len(file_bytes)
    return doc_id, clean_name, file_path, file_size

def delete_stored_file(file_path: str):
    """Safely delete stored file."""
    if file_path and os.path.exists(file_path):
        real_target = os.path.abspath(file_path)
        real_upload_dir = os.path.abspath(UPLOAD_DIR)
        if real_target.startswith(real_upload_dir):
            try:
                os.remove(file_path)
            except OSError:
                pass
