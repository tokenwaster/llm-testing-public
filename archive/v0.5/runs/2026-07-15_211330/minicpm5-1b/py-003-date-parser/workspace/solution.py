import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    # Validate input format using regex patterns
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # ISO format
        r'^(\d{1,2})/(\d{1,2})/(\d{4})$',  # day/month/year with slashes
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b',  # month name (case-insensitive)
        r'^(\d{1,2})\s*([A-Za-z]+)\s*(\d{4})$'  # day/month abbreviation
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text.strip())
        if not match:
            continue
        
        # Extract components from the matched string
        parts = match.groups()
        
        # Handle each format separately
        if len(parts) == 4 and parts[0] == '2024':
            # ISO format: already valid
            return f"{parts[1]}-{parts[2]}-{parts[3]}"
        elif len(parts) == 5 and parts[0] in ['05', '03']:
            # Day/month/year with zero-padded or not
            day = int(parts[1])
            month_abbr = parts[2]
            year = int(parts[4])
            # Validate date using datetime (allowed since stdlib is allowed)
            try:
                dt = datetime(year, month_abbr, day)
                return f"{dt.year}-{dt.month_abbr}-{dt.day}"
            except ValueError:
                continue
        elif len(parts) == 3 and parts[0] in ['March', 'May', 'July', 'August', 'September', 'October', 'November', 'December']:
            # Month name (case-insensitive)
            month_name = parts[2].lower()
            if month_name not in ["january", "february", "march", "april", "may", "june",
                                     "july", "august", "september", "october", "november", "december"]:
                continue
            # Validate date using datetime (allowed since stdlib is allowed)
            try:
                dt = datetime(year=parts[1], month=month_name, day=int(parts[2]))
                return f"{dt.year}-{dt.month}-{dt.day}"
            except ValueError:
                continue
        elif len(parts) == 4 and parts[0] in ['5', 'Mar']:
            # Day/month abbreviation with zero-padded or not
            day = int(parts[1])
            month_abbr = parts[2]
            year = int(parts[3])
            try:
                dt = datetime(year, month_abbr, day)
                return f"{dt.year}-{dt.month_abbr}-{dt.day}"
            except ValueError:
                continue
    
    return None
