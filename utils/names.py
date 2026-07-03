import re
from config import NON_NAME_WORDS

_NAME_INTRO = re.compile(
    r"(?:my name is|i am|this is|i'm|myself|name\s*[:\-]\s*)"
    r"\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})",
    re.IGNORECASE,
)
_SALUTATION_NAME = re.compile(
    r"(?:hi|hello|hey)[,\s]+(?:i(?:'m| am)\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
    re.IGNORECASE,
)
_PROPER_NAME = re.compile(r'\b([A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20}){1,3})\b')


def extract_names_from_text(text: str) -> list:
    candidates, seen = [], set()

    def add(name: str):
        name  = name.strip()
        parts = name.split()
        if len(parts) < 2:
            return
        if any(p.lower() in NON_NAME_WORDS for p in parts):
            return
        key = name.lower()
        if key not in seen:
            seen.add(key)
            candidates.append(name)

    for m in _NAME_INTRO.finditer(text):
        add(m.group(1))
    for m in _SALUTATION_NAME.finditer(text):
        add(m.group(1))
    for m in _PROPER_NAME.finditer(text):
        add(m.group(1))

    return candidates