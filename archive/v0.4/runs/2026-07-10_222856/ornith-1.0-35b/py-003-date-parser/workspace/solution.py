from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    formats = [
        '%Y-%m-%d',      # ISO format (YYYY-MM-DD)
        '%d/%m/%Y',      # Day/Month/Year with slashes
        '%B %d, %Y',     # Full month name, day, comma, year
        '%d %b %Y',      # Day, abbreviated month, year
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None
