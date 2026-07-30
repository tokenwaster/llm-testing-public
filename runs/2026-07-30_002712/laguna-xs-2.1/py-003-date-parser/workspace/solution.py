import datetime
from datetime import date
import re

months_full = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

months_abbrev = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def normalize_date(text: str) -> str | None:
    stripped_text = text.strip()
    
    # Case 1: ISO format (YYYY-MM-DD)
    try:
        dt = datetime.datetime.strptime(stripped_text, "%Y-%m-%d")
        return stripped_text
    except ValueError:
        pass

    # Case 2: D/M/Y with slashes
    parts_slash = stripped_text.split('/')
    if len(parts_slash) == 3:
        day_str = parts_slash[0].strip()
        month_str = parts_slash[1].strip()
        year_str = parts_slash[2].strip()
        
        try:
            day = int(day_str)
            month_num = int(month_str)
            year = int(year_str)
            dt = datetime.date(year, month_num, day)
            return dt.isoformat()
        except (ValueError, TypeError):
            pass

    # Case 3: "Month Day, Year" format
    if ',' in stripped_text:
        parts_comma = stripped_text.split(',', maxsplit=1)
        first_part = parts_comma[0].strip()
        second_part_str = parts_comma[1].strip() if len(parts_comma) > 1 else ""
        
        if re.fullmatch(r'\d{4}', second_part_str):
            year = int(second_part_str)
            tokens_day_month = first_part.split()
            if len(tokens_day_month) == 2:
                month_token_lower = tokens_day_month[0].strip().lower()
                day_token = tokens_day_month[1]
                
                if month_token_lower in months_full:
                    try:
                        day = int(day_token.strip())
                        month_num = months_full[month_token_lower]
                        dt = datetime.date(year, month_num, day)
                        return dt.isoformat()
                    except ValueError:
                        pass

    # Case 4: "D Mon YYYY" format
    parts_space = stripped_text.split()
    if len(parts_space) == 3:
        day_str_part, month_abbrev_part, year_str_part = [s.strip() for s in parts_space]
        
        try:
            day = int(day_str_part)
            month_abbr_lower = month_abbrev_part.lower()
            year = int(year_str_part)
            
            if len(year_str_part) == 4 and month_abbr_lower in months_abbrev:
                month_num = months_abbrev[month_abbr_lower]
                dt = datetime.date(year, month_num, day)
                return dt.isoformat()
        except ValueError:
            pass

    return None
