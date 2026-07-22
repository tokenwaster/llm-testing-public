import datetime
import re

def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None
        
    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY or D/M/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.fullmatch(r'([A-Za-z]+) (\d{1,2}), (\d{4})', text)
    if m:
        month = _month_to_num(m.group(1).lower())
        if month:
            try:
                return datetime.date(int(m.group(3)), month, int(m.group(2))).isoformat()
            except ValueError:
                return None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r'(\d{1,2}) ([A-Za-z]+) (\d{4})', text)
    if m:
        month = _month_to_num(m.group(2).lower())
        if month:
            try:
                return datetime.date(int(m.group(3)), month, int(m.group(1))).isoformat()
            except ValueError:
                return None
                
    return None

def _month_to_num(month_str: str) -> int | None:
    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    return months.get(month_str)
