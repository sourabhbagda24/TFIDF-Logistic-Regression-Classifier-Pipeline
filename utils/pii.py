import re

PATTERNS = {
    "EMAIL":    re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'),
    "CARD":     re.compile(r'\b(?:\d[ \-]*?){13,16}\b'),
    "AADHAAR":  re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b'),
    "PAN":      re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b'),
    "IFSC":     re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b'),
    "ACCOUNT":  re.compile(r'\b\d{9,18}\b'),
    "PHONE":    re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}\b'),
    "PIN_CODE": re.compile(r'\b\d{6}\b'),
    "URL":      re.compile(r'https?://\S+|www\.\S+'),
}

PII_ORDER = ["EMAIL", "CARD", "AADHAAR", "PAN", "IFSC", "ACCOUNT", "PHONE", "PIN_CODE"]

MASK_TAGS = {
    "EMAIL":    "[EMAIL]",
    "CARD":     "[CARD]",
    "AADHAAR":  "[AADHAAR]",
    "PAN":      "[PAN]",
    "IFSC":     "[IFSC]",
    "ACCOUNT":  "[ACCOUNT]",
    "PHONE":    "[PHONE]",
    "PIN_CODE": "[PINCODE]",
    "URL":      "[URL]",
}


def find_pii(text: str) -> list:
    found = []
    for t in PII_ORDER:
        for m in PATTERNS[t].finditer(text):
            found.append({"type": t, "value": m.group()})
    return found


def mask_text(text: str) -> str:
    out = text
    for k in PII_ORDER:
        out = PATTERNS[k].sub(MASK_TAGS[k], out)
    return out


def normalize(pii_type: str, value: str) -> str:
    if pii_type in ("PHONE", "ACCOUNT", "CARD", "AADHAAR", "PIN_CODE"):
        cleaned = re.sub(r'\D', '', value)
        if pii_type == "PHONE" and len(cleaned) > 10:
            cleaned = cleaned[-10:]
        return cleaned
    return value.strip()