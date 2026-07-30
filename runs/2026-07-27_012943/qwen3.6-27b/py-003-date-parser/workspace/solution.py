import re
from datetime import date

def normalize_date(text: str) -> str | None:
    # Strip surrounding whitespace as per requirements
    s = text.strip()
    if not s:
        return None

    # Dictionary for full English month names
    full_months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    
    # Dictionary for 3-letter English month abbreviations
    # Note: "May" is included as it is a 3-letter string representing a month
    abbrev_months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    # Format 1: YYYY-MM-DD (ISO)
    # Strictly matches the example "2024-03-05"
    iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if iso_match:
        try:
            y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
            # Validate the date
            date(y, m, d)
            return s
        except ValueError:
            return None

    # Format 2: DD/MM/YYYY
    # Slashes, zero-padded or not
    slash_match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if slash_match:
        try:
            d = int(slash_match.group(1))
            m = int(slash_match.group(2))
            y = int(slash_match.group(3))
            # Validate the date
            d_obj = date(y, m, d)
            return d_obj.isoformat()
        except ValueError:
            return None

    # Text formats
    # Check for comma to distinguish Format 3 (Month DD, YYYY)
    if ',' in s:
        # Format 3: Month DD, YYYY
        # Regex expects: Word (Month) Space(s) Digit(s) (Day) Space(s) Comma Space(s) 4-Digits (Year)
        comma_match = re.match(r'^([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})$', s)
        if comma_match:
            month_str = comma_match.group(1)
            d = int(comma_match.group(2))
            y = int(comma_match.group(3))
            
            # Check if month_str is a valid full month name
            if month_str.lower() in full_months:
                m = full_months[month_str.lower()]
                try:
                    d_obj = date(y, m, d)
                    return d_obj.isoformat()
                except ValueError:
                    return None
            # Comma present but invalid month name or format
            return None
        # Comma present but regex mismatch
        return None

    # Format 4: DD Month YYYY
    # No comma (checked above)
    # Regex expects: Digit(s) (Day) Space(s) Word (Month) Space(s) 4-Digits (Year)
    text_match = re.match(r'^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$', s)
    if text_match:
        d = int(text_match.group(1))
        month_str = text_match.group(2)
        y = int(text_match.group(3))
        
        # Check if month_str is a valid 3-letter abbreviation
        if month_str.lower() in abbrev_months:
            m = abbrev_months[month_str.lower()]
            try:
                d_obj = date(y, m, d)
                return d_obj.isoformat()
            except ValueError:
                return None
        # Format mismatch (invalid month name for this format)
        return None

    # No format matched
    return None
