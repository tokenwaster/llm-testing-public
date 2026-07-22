from datetime import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    # Format 1: ISO format YYYY-MM-DD
    if len(text) == 10 and text[4] == '-' and text[7] == '-':
        try:
            dt = datetime.strptime(text, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Format 2: day/month/year (D/M/YYYY or DD/MM/YYYY)
    if '/' in text and ',' not in text:
        parts = text.split('/')
        if len(parts) == 3:
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                dt = datetime(year, month, day)
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
    
    # Format 3: "Month D, YYYY"
    if ',' in text:
        try:
            dt = datetime.strptime(text, '%B %d, %Y')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Format 4: "D Mon YYYY"
    if '/' not in text and ',' not in text:
        parts = text.split()
        if len(parts) == 3:
            try:
                day = int(parts[0])
                month_str = parts[1].lower()
                year = int(parts[2])
                
                dt = datetime.strptime(f"{day} {month_str} {year}", "%d %b %Y")
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
    
    return None
