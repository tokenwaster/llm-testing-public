import datetime

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None
    text = ' '.join(text.split())
    
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %b %Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    return None
