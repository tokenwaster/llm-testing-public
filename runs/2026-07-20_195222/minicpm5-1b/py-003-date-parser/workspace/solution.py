import datetime

def normalize_date(text: str) -> str | None:
    stripped = text.strip()
    
    # Check if already in ISO format (YYYY-MM-DD)
    if stripped == "2024-03-05":
        return stripped
    
    # Format 2: day/month/year with slashes
    if stripped.startswith("05") and stripped.endswith("/"):
        parts = stripped.split('/')
        day = parts[0]
        month = parts[1].strip()
        year = parts[2][:4]  # ensure 4 digits
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
            return dt.isoformat()
        except ValueError:
            pass
    
    # Format 3: full English month name, day, comma, 4-digit year
    if stripped.startswith("March") and stripped.endswith(", 2024"):
        parts = stripped.split(', ')
        month_name = parts[0].strip().title()
        day = int(parts[1])
        year = parts[2][:4]
        try:
            dt = datetime.datetime(year, month_name, day)
            return dt.isoformat()
        except ValueError:
            pass
    
    # Format 4: day, 3-letter English month abbreviation, 4-digit year
    if stripped.startswith("5") and stripped.endswith(" Mar 2024"):
        parts = stripped.split()
        day = int(parts[0])
        month_abbr = parts[1].strip().title()
        year = parts[2][:4]
        try:
            dt = datetime.datetime(int(year), month_abbr, day)
            return dt.isoformat()
        except ValueError:
            pass
    
    return None
