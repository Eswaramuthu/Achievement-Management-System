import re
from datetime import datetime

def parse_certificate_text(text):
    """
    Extract structured data (name, event, date)
    from raw OCR text using rule-based regex.
    """

    parsed_data = {
        "student_name": None,
        "event_name": None,
        "achievement_date": None
    }

    if not text:
        return parsed_data

    # -------------------------
    # Try extracting name
    # -------------------------
    name_patterns = [
        r"Presented to\s+(.*)",
        r"Awarded to\s+(.*)",
        r"This certifies that\s+(.*)"
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed_data["student_name"] = match.group(1).strip()
            break

    # -------------------------
    # Try extracting date
    # -------------------------
    date_patterns = [
        r"\b(\d{1,2}\s+\w+\s+\d{4})\b",
        r"\b(\d{2}/\d{2}/\d{4})\b"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            parsed_data["achievement_date"] = match.group(1)
            break

    # -------------------------
    # Try extracting event name
    # -------------------------
    event_patterns = [
        r"for participating in\s+(.*)",
        r"in recognition of\s+(.*)",
        r"for\s+(.*)\s+held at"
    ]

    for pattern in event_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed_data["event_name"] = match.group(1).strip()
            break

    return parsed_data
