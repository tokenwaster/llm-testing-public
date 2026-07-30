from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None

    text = text.strip()
    if not text:
        return None

    formats = [
        "%Y-%m-%d",   # 2024-03-05
        "%d/%m/%Y",   # 05/03/2024 or 5/3/2024
        "%B %d, %Y",  # March 5, 2024
        "%d %b %Y",   # 5 Mar 2024
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
