import re
import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None

    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    # Format 1: YYYY-MM-DD
    if m := re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', text):
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    if m := re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text):
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month DD, YYYY
    if m := re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text):
        month_name = m.group(1).lower()
        if month_name in months:
            try:
                return datetime.date(int(m.group(3)), months[month_name], int(m.group(2))).isoformat()
            except ValueError:
                return None

    # Format 4: DD Mon YYYY
    if m := re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text):
        month_name = m.group(2).lower()
        if month_name in months:
            try:
                return datetime.date(int(m.group(3)), months[month_name], int(m.group(1))).isoformat()
            except ValueError:
                return None

    return None
