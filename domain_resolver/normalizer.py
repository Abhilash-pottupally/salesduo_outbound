import re
import unicodedata


def normalize_brand(value: str) -> str:
    """Normalize a brand for matching without destroying the original value."""
    value = unicodedata.normalize("NFKC", value or "")
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()
