import datetime
import re

def normalize_date(text: str) -> str | None:
    s = text.strip()
    if not s:
        return None

    # 1. ISO format YYYY-MM-DD
    try:
        datetime.date.fromisoformat(s)
        return s
    except ValueError:
        pass

    # 2. DD/MM/YYYY
    match = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if match:
        day, month, year = map(int, match.groups())
        try:
            dt = datetime.date(year, month, day)
            return dt.isoformat()
        except ValueError:
            return None

    # 3. Full month name: "MonthName Day, Year"
    match = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', s)
    if match:
        month_name, day_str, year_str = match.groups()
        month_name = month_name.lower()
        month_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        if month_name in month_map:
            month = month_map[month_name]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None
        else:
            return None

    # 4. Abbreviated month: "Day Mon Year"
    match = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', s)
    if match:
        day_str, month_abbr, year_str = match.groups()
        month_abbr = month_abbr.lower()
        abbr_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        if month_abbr in abbr_map:
            month = abbr_map[month_abbr]
            day = int(day_str)
            year = int(year_str)
            try:
                dt = datetime.date(year, month, day)
                return dt.isoformat()
            except ValueError:
                return None
        else:
            return None

    return None
