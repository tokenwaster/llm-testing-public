import re
from datetime import date

def normalize_date(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None

    months = ["january", "february", "march", "april", "may", "june", 
              "july", "august", "september", "october", "november", "december"]
    month_abbrs = [m[:3] for m in months]

    # Format 1: YYYY-MM-DD
    if m := re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', text):
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    if m := re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text):
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month DD, YYYY
    if m := re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})', text):
        month_name = m.group(1).lower()
        if month_name in months:
            try:
                return date(int(m.group(3)), months.index(month_name) + 1, int(m.group(2))).isoformat()
            except ValueError:
                return None
        return None

    # Format 4: DD Mon YYYY
    if m := re.fullmatch(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text):
        month_name = m.group(2).lower()
        if month_name in month_abbrs:
            try:
                return date(int(m.group(3)), month_abbrs.index(month_name) + 1, int(m.group(1))).isoformat()
            except ValueError:
                return None
        return None

    return None
