import re
import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    MONTH_ABBRS = [m[:3] for m in MONTH_NAMES]
    
    # Format 1: YYYY-MM-DD
    m = re.fullmatch(r'(\d{4})-(\d{1,2})-(\d{1,2})', text)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return None

    # Format 3: Month D, YYYY
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', text)
    if m:
        month_str, day_str, year_str = m.groups()
        day, year = int(day_str), int(year_str)
        month_num = None
        for i, name in enumerate(MONTH_NAMES, 1):
            if name.lower() == month_str.lower():
                month_num = i
                break
        if month_num:
            try:
                return datetime.date(year, month_num, day).isoformat()
            except ValueError:
                return None
        return None

    # Format 4: D Mon YYYY
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        day_str, month_str, year_str = m.groups()
        day, year = int(day_str), int(year_str)
        month_num = None
        for i, abbr in enumerate(MONTH_ABBRS, 1):
            if abbr.lower() == month_str.lower():
                month_num = i
                break
        if month_num:
            try:
                return datetime.date(year, month_num, day).isoformat()
            except ValueError:
                return None
        return None

    return None
