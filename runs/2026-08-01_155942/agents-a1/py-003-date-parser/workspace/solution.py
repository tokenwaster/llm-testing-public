import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Mapping for month names (case-insensitive lookup)
    # Includes both full names and standard abbreviations to handle variations robustly
    MONTHS_MAP = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 
        'may': 5, 'june': 6, 'july': 7, 'august': 8, 
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        # Abbreviations (3 letters usually)
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    def validate_and_format(y: int, m: int, d: int) -> str | None:
        try:
            # Constructing a date object validates the calendar (e.g. Feb 31 throws ValueError)
            dt = date(int(y), int(m), int(d))
            return f"{dt.year:04}-{dt.month:02}-{dt.day:02}"
        except ValueError:
            return None

    # Format 1: ISO YYYY-MM-DD (Dashes, Year-Month-Day)
    m_iso = re.match(r'^(\d{4})-(\d+)-(\d+)$', text)
    if m_iso:
        y, m, d = m_iso.group(1), m_iso.group(2), m_iso.group(3)
        return validate_and_format(y, m, d)

    # Format 2: Slash DD/MM/YYYY or D/M/Y (Day-Month-Year)
    if re.match(r'^(\d+)/(\d+)/(\d{4})$', text):
        parts = re.search(r'^(\d+)/(\d+)/(\d{4})$', text).groups()
        d, m, y = parts[0], parts[1], parts[2]
        return validate_and_format(y, m, d)

    # Format 3: Full English month name First [Month] [Day] [Year] (or with comma)
    if re.match(r'^([A-Za-z]+)\s+(\d+)\s*,?\s*(\d{4})$', text):
        groups = re.search(r'^([A-Za-z]+)\s+(\d+)\s*,?\s*(\d{4})$', text).groups()
        month_str, day_str, year_str = groups[0].lower(), groups[1], groups[2]
        
        if month_str in MONTHS_MAP:
            return validate_and_format(year_str, str(MONTHS_MAP[month_str]), day_str)

    # Format 4: Day First [Day] [Month Abbr/Name] [Year] (space separated)
    if re.match(r'^(\d+)\s+([A-Za-z]+)\s+(\d{4})$', text):
        groups = re.search(r'^(\d+)\s+([A-Za-z]+)\s+(\d{4})$', text).groups()
        day_str, month_str, year_str = groups[0], groups[1].lower(), groups[2]
        
        if month_str in MONTHS_MAP:
            return validate_and_format(year_str, str(MONTHS_MAP[month_str]), day_str)

    # No format matched or date is invalid
    return None
