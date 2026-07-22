import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: YYYY-MM-DD (ISO format)
    try:
        dt = datetime.datetime.strptime(text, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Format 2: DD/MM/YYYY or D/M/YYYY with slashes
    for fmt in ["%d/%m/%Y", "%d/%m/%y"]:
        try:
            dt = datetime.datetime.strptime(text, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # Format 3: Month DD, YYYY (full month name) - e.g., "March 5, 2024"
    try:
        dt = datetime.datetime.strptime(text, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Format 4: D MMM YYYY (abbreviated month) - e.g., "5 Mar 2024"
    try:
        dt = datetime.datetime.strptime(text, "%d %b %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # Also try with day having leading space for format 3/4 variations
    try:
        dt = datetime.datetime.strptime(text, "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    return None
