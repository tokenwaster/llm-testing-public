import re
from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()

    # Case 1: already ISO format (YYYY-MM-DD)
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        try:
            dt = datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            return None

    # Case 2: day/month/year with slashes (d/m/y)
    if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', text):
        try:
            dt = datetime.strptime(text, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Case 3: Full month name (e.g., "March 5, 2024")
    case3_match = re.fullmatch(r'([A-Za-z]+)\s+(\d+),\s*(\d{4})', text)
    if case3_match:
        try:
            month_name, day_str, year_str = case3_match.groups()
            month_lower = month_name.lower()
            months_dict = {
                'january': 1,
                'february': 2,
                'march': 3,
                'april': 4,
                'may': 5,
                'june': 6,
                'july': 7,
                'august': 8,
                'september': 9,
                'october': 10,
                'november': 11,
                'december': 12
            }
            if month_lower not in months_dict:
                return None
            day = int(day_str)
            year = int(year_str)
            month = months_dict[month_lower]
            dt = datetime(year, month, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # Case 4: Day, three-letter abbreviation, year (e.g., "5 Mar 2024")
    case4_match = re.fullmatch(r'(\d+)\s+([A-Za-z]{3})\s+(\d{4})', text)
    if case4_match:
        try:
            day_str, month_abbr, year_str = case4_match.groups()
            month_lower = month_abbr.lower()
            abbrev_months = {
                'jan': 1,
                'feb': 2,
                'mar': 3,
                'apr': 4,
                'may': 5,
                'jun': 6,
                'jul': 7,
                'aug': 8,
                'sep': 9,
                'oct': 10,
                'nov': 11,
                'dec': 12
            }
            if month_lower not in abbrev_months:
                return None
            day = int(day_str)
            year = int(year_str)
            month = abbrev_months[month_lower]
            dt = datetime(year, month, day)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None

    # If none of the cases matched
    return None
