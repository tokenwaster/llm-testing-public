import datetime


def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    if not text:
        return None
    
    # Try ISO format: YYYY-MM-DD
    if '-' in text and len(text) == 10:
        try:
            parts = text.split('-')
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            date_obj = datetime.date(year, month, day)
            return text
        except (ValueError, IndexError):
            pass
    
    # Try DD/MM/YYYY with slashes
    if '/' in text:
        parts = text.split('/')
        if len(parts) == 3:
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                date_obj = datetime.date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
            except (ValueError, IndexError):
                pass
    
    # Try Month DD, YYYY format (full month name with comma)
    if ',' in text:
        parts = text.split(',')
        if len(parts) == 2:
            month_name, rest = parts[0].strip(), parts[1].strip()
            try:
                year_part, day_part = rest.rsplit(None, 1)
                day = int(day_part.strip())
                year = int(year_part.strip())
                date_obj = datetime.date(year, month_name.lower(), day)
                return f"{year:04d}-{month_name.month:02d}-{day:02d}"
            except (ValueError, IndexError):
                pass
    
    # Try DD Mon YYYY format (abbreviated or full month name)
    if len(text.split()) == 3:
        parts = text.split()
        try:
            day = int(parts[0])
            month_str = parts[1].lower()
            year = int(parts[2])
            
            # Month mapping (abbreviations and full names)
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'june': 6, 'july': 7, 'august': 8, 'september': 9,
                'october': 10, 'november': 11, 'december': 12
            }
            
            if month_str in month_map:
                month = month_map[month_str]
                date_obj = datetime.date(year, month, day)
                return f"{year:04d}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            pass
    
    return None
