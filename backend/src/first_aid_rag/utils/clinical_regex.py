import re
from typing import Optional, Tuple


PAGE_NUMBER_PATTERN = re.compile(
    r"^(?:page\s+)?\d+(?:\s*(?:of|/)\s*\d+)?$",
    re.IGNORECASE,
)

BOILERPLATE_PATTERNS = [
    re.compile(r"©|copyright|all rights reserved", re.IGNORECASE),
    re.compile(r"downloaded from|accessed on|retrieved from", re.IGNORECASE),
    re.compile(r"first aid guidelines|resuscitation council|european resuscitation", re.IGNORECASE),
    re.compile(r"for personal use only|do not distribute", re.IGNORECASE),
]

NICE_REC_PATTERN = re.compile(
    r"\b(?:NICE|CG\d+|NG\d+|QS\d+)?\s*(?:Recommendation|Rec\.?)\s*(\d+(?:\.\d+)*)\b",
    re.IGNORECASE,
)

ESC_CLASS_PATTERN = re.compile(
    r"\bClass\s+(I{1,3}|IV|[1-4]|II[ab]|II[AB])\b",
    re.IGNORECASE,
)

ESC_LEVEL_PATTERN = re.compile(
    r"\bLevel\s+(?:of\s+evidence\s+)?([A-C])\b",
    re.IGNORECASE,
)


def is_page_number_text(text: str) -> bool:
    """Return True if text consists solely of a page number or page counter."""
    clean = text.strip()
    if not clean:
        return False
    return bool(PAGE_NUMBER_PATTERN.match(clean)) or (clean.isdigit() and len(clean) <= 4)


def is_boilerplate_text(text: str) -> bool:
    """Return True if text matches common publication boilerplate or copyright notices."""
    clean = text.strip()
    if not clean:
        return False
    return any(bool(p.search(clean)) for p in BOILERPLATE_PATTERNS)


def extract_nice_recommendation_id(text: str) -> Optional[str]:
    """Extract NICE recommendation identifier (e.g. '1.2.3') if present."""
    match = NICE_REC_PATTERN.search(text)
    return match.group(1) if match else None


def extract_esc_metadata(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract ESC Class (e.g. 'I', 'IIa') and Level of Evidence (e.g. 'A', 'B', 'C')."""
    class_match = ESC_CLASS_PATTERN.search(text)
    level_match = ESC_LEVEL_PATTERN.search(text)
    esc_class = class_match.group(1).upper() if class_match else None
    esc_level = level_match.group(1).upper() if level_match else None
    return esc_class, esc_level

