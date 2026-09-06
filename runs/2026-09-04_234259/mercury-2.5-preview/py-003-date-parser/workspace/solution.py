from datetime import datetime

def normalize_date(text: str) -> str | None:
    if not text:
        return None
    
    text = text.strip()
    if not text:
        return None

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %b %Y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
