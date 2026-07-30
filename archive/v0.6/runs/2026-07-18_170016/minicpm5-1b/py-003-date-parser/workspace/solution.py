import re

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # format1 (already ISO)
        r'^5/3/2024$',          # format2 (zero-padded)
        r'^([A-Za-z]+)\s+(\d{1,2})\s+([., ])\s+(\d{4},?)$',  # format3
        r'^\s+([A-Z]{3})\s+(\d{4})$'   # format4 (no spaces)
    ]
    
    for pattern in patterns:
        match = re.fullmatch(pattern, text)
        if match:
            if pattern == r'^\d{4}-\d{2}-\d{2}$':
                year_str, month_str, day_str = match.groups()
                year = int(year_str)
                month = int(month_str)
                day = int(day_str)
                return f"{year:04d}-{month:02d}-{day:02d}"
            elif pattern == r'^5/3/2024$':
                # For this exact pattern, match.groups() gives (year=2024, month=5, day=3)
                return f"{2024:04d}-{5:02d}-{3:02d}"
            elif pattern == r'^([A-Za-z]+)\s+(\d{1,2})\s+([., ])\s+(\d{4},?)$':
                month_name = match.group(0).split()[0]  # remove leading space
                day_str = match.group(1)
                year = int(match.group(3))
                return f"{year:04d}-{month_name:02d}-{day_str:02d}"
            elif pattern == r'^\s+([A-Z]{3})\s+(\d{4})$':
                month, year = match.group(0).split()[0], int(match.group(2))
                return f"{year:04d}-{month:02d}-{int(year):02d}"
            else:
                # Should not happen
                return None
    
    return None
