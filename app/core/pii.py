import re

_PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def redact_pii(text: str) -> tuple[str, int]:
    count = 0
    for label, pattern in _PATTERNS.items():
        text, n = pattern.subn(f"[REDACTED_{label}]", text)
        count+=n
    return text, count

def redact_dict_vals(data):
    count = 0
    def _walk(value):
        nonlocal count
        if isinstance(value, str):
            redacted, n = redact_pii(value)
            count+=n
            return redacted
        if isinstance(value, dict):
            return {k: _walk(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_walk(v) for v in value]
        return value
    return _walk(data), count