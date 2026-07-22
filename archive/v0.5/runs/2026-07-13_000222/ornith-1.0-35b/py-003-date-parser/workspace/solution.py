import re
from datetime import datetime


def normalize_date(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO)
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return text
        except ValueError:
            return None
    
    # Format 2: DD/MM/YYYY or D/M/YYYY (day/month/year with slashes)
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            datetime(year=year, month=month, day=day)
            return f'{year:04d}-{month:02d}-{day:02d}'
        except ValueError:
            return None
    
    # Format 3: "March 5, 2024" — full English month name, day, comma, year
    m = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', text)
    if m:
        month_str, day_str, year_str = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime.strptime(f'{month_str} {day_str}, {year_str}', '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Format 4: "5 Mar 2024" — day, 3-letter month abbreviation, year
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
    if m:
        day_str, month_str, year_str = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime.strptime(f'{day_str} {month_str} {year_str}', '%d %b %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    return None
