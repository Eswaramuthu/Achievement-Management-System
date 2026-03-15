import hashlib
from utils.certificate_ocr import extract_text_from_certificate
from utils.certificate_parser import parse_certificate_text


def generate_file_hash(file_path):
    """
    Generate SHA256 hash for duplicate detection.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()


def process_certificate(file_path):
    """
    Orchestrates:
    - OCR
    - Parsing
    - Hash generation
    """
    raw_text = extract_text_from_certificate(file_path)
    parsed_data = parse_certificate_text(raw_text)
    file_hash = generate_file_hash(file_path)

    return {
        "raw_text": raw_text,
        "parsed_data": parsed_data,
        "file_hash": file_hash
    }
