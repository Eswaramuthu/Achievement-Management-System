import re
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ── Pattern banks ─────────────────────────────────────────────────────────────

NAME_PATTERNS: list[str] = [
    r"(?:Presented|Awarded)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    r"This\s+certifies\s+that\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    r"(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
]

DATE_PATTERNS: list[tuple[str, str]] = [
    # pattern                                  # strptime format
    (r"\b(\d{1,2}\s+\w+\s+\d{4})\b",          "%d %B %Y"),
    (r"\b(\d{2}/\d{2}/\d{4})\b",              "%d/%m/%Y"),
    (r"\b(\d{4}-\d{2}-\d{2})\b",              "%Y-%m-%d"),   # ← ISO 8601 added
    (r"\b(\d{1,2}-\w+-\d{4})\b",              "%d-%B-%Y"),   # ← e.g. 01-January-2024
]

EVENT_PATTERNS: list[str] = [
    r"for\s+participating\s+in\s+(.*?)(?:\s+held|\s+on|\s+at|$)",
    r"in\s+recognition\s+of\s+(.*?)(?:\s+held|\s+on|\s+at|$)",
    r"for\s+(.*?)\s+held\s+at",
    r"(?:competition|event|tournament|conference|workshop)[:\s]+([^\n.]+)",  # ← added
]


# ── Result type ───────────────────────────────────────────────────────────────

class ParsedCertificate:
    """Structured result returned by :func:`parse_certificate_text`."""

    def __init__(
        self,
        student_name: Optional[str] = None,
        event_name:   Optional[str] = None,
        achievement_date: Optional[datetime] = None,
        raw_date_string: Optional[str] = None,
    ) -> None:
        self.student_name     = student_name
        self.event_name       = event_name
        self.achievement_date = achievement_date   # parsed datetime, or None
        self.raw_date_string  = raw_date_string    # original string before parsing

    def to_dict(self) -> dict:
        """
        Serialise to a plain dictionary (safe for JSON / DB insertion).

        Returns:
            dict with keys student_name, event_name, achievement_date,
            and raw_date_string.
        """
        return {
            "student_name":     self.student_name,
            "event_name":       self.event_name,
            "achievement_date": (
                self.achievement_date.strftime("%Y-%m-%d")
                if self.achievement_date else None
            ),
            "raw_date_string":  self.raw_date_string,
        }

    def is_complete(self) -> bool:
        """Return True only when all three core fields were successfully extracted."""
        return all([self.student_name, self.event_name, self.achievement_date])


# ── Private helpers ───────────────────────────────────────────────────────────

def _extract_name(text: str) -> Optional[str]:
    """
    Scan *text* for a human name using :data:`NAME_PATTERNS`.

    Args:
        text: Raw OCR string.

    Returns:
        Capitalised full name, or ``None`` if no pattern matched.
    """
    for pattern in NAME_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()
    return None


def _extract_date(text: str) -> tuple[Optional[datetime], Optional[str]]:
    """
    Scan *text* for a date and parse it to a :class:`datetime`.

    Tries every ``(pattern, fmt)`` pair in :data:`DATE_PATTERNS` in order.

    Args:
        text: Raw OCR string.

    Returns:
        ``(datetime_object, raw_string)`` on success,
        ``(None, None)`` if nothing matched or parsing failed.
    """
    for pattern, fmt in DATE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1)
            try:
                return datetime.strptime(raw, fmt), raw
            except ValueError:
                logger.debug("Date string %r matched pattern but failed strptime(%r)", raw, fmt)
                continue   # try next pattern instead of silently dropping
    return None, None


def _extract_event(text: str) -> Optional[str]:
    """
    Scan *text* for an event / competition name using :data:`EVENT_PATTERNS`.

    Args:
        text: Raw OCR string.

    Returns:
        Stripped event name, or ``None`` if no pattern matched.
    """
    for pattern in EVENT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(".,;")
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def parse_certificate_text(text: str) -> ParsedCertificate:
    """
    Extract structured data from raw OCR certificate text.

    Uses rule-based regex matching.  Each field is attempted independently
    so a failure in one field does not affect the others.

    Args:
        text: Raw string produced by an OCR engine.

    Returns:
        A :class:`ParsedCertificate` instance.  Unextracted fields are
        ``None``; call :meth:`ParsedCertificate.is_complete` to check.

    Example::

        result = parse_certificate_text(ocr_output)
        if result.is_complete():
            db.insert(result.to_dict())
        else:
            flag_for_manual_review(result)
    """
    if not text or not text.strip():
        logger.warning("parse_certificate_text received empty input")
        return ParsedCertificate()

    # Normalise whitespace (OCR often produces irregular spacing)
    normalised = re.sub(r"\s+", " ", text).strip()

    date_obj, raw_date = _extract_date(normalised)

    result = ParsedCertificate(
        student_name     = _extract_name(normalised),
        event_name       = _extract_event(normalised),
        achievement_date = date_obj,
        raw_date_string  = raw_date,
    )

    if not result.is_complete():
        logger.info(
            "Incomplete parse — name=%s, event=%s, date=%s",
            result.student_name, result.event_name, result.achievement_date,
        )

    return result