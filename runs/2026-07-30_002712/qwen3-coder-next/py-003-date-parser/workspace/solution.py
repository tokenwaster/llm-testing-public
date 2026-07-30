from datetime import datetime
import calendar

def normalize_date(text: str | None) -> str | None:
    if text is None:
        return None
    
    # Strip surrounding whitespace
    text = text.strip()
    
    if not text:
        return None
    
    # Try format 1: ISO format YYYY-MM-DD (already validated)
    try:
        parts = text.split('-')
        if len(parts) == 3:
            year, month, day = map(int, parts)
            datetime(year, month, day)  # validate date
            # Check that the original string matches the expected format (YYYY-MM-DD)
            if len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        pass
    
    # Try format 2: DD/MM/YYYY or D/M/YYYY etc with slashes
    try:
        parts = text.split('/')
        if len(parts) == 3:
            day, month, year = map(int, parts)
            datetime(year, month, day)  # validate date
            return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        pass
    
    # Try format 3: Month DD, YYYY (e.g., "March 5, 2024")
    month_names = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    
    try:
        # Split by space and comma
        parts = text.replace(',', ' ').split()
        if len(parts) == 3:
            month_str, day_str, year_str = parts[0].lower(), parts[1], parts[2]
            
            # Find the month index (1-12)
            for i, m_name in enumerate(month_names):
                if month_str.startswith(m_name[:len(month_str)]):  # handle partial match
                    month = i + 1
                    break
            else:
                month = None
                
            if month is not None:
                day = int(day_str)
                year = int(year_str)
                datetime(year, month, day)  # validate date
                return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        pass
    
    # Try format 4: DD Mon YYYY (e.g., "5 Mar 2024")
    month_abbr = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]
    
    try:
        parts = text.split()
        if len(parts) == 3:
            day_str, month_str, year_str = parts[0], parts[1].lower(), parts[2]
            
            # Find the month index (1-12)
            for i, m_abbr in enumerate(month_abbr):
                if month_str.startswith(m_abbr[:len(month_str)]):  # handle partial match
                    month = i + 1
                    break
            else:
                month = None
                
            if month is not None:
                day = int(day_str)
                year = int(year_str)
                datetime(year, month, day)  # validate date
                return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        pass
    
    # If none of the formats worked, return None
    return None
