import datetime

def normalize_date(text: str) -> str | None:
    text = text.strip()
    
    if not text:
        return None
    
    # Month name mappings
    month_names = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    month_abbr = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    def parse_iso(text: str) -> bool:
        try:
            datetime.datetime.strptime(text, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def parse_day_month_year_slash(text: str) -> datetime.date | None:
        try:
            parsed = datetime.datetime.strptime(text, "%d/%m/%Y")
            return parsed.date()
        except ValueError:
            pass
        try:
            parsed = datetime.datetime.strptime(text, "%d-%m-%Y")
            return parsed.date()
        except ValueError:
            pass
        try:
            parsed = datetime.datetime.strptime(text, "%m/%d/%Y")
            # Verify it's actually day/month/year by checking day > month for non-1st months logic won't work
            # Better to just accept all but that's incorrect - let's stick to d/m/Y as specified
            return None
        except ValueError:
            pass
        return None
    
    def parse_day_full_month_year(text: str) -> datetime.date | None:
        parts = text.split(',')
        if len(parts) != 2:
            return None
        day_part, year_part = parts
        
        day_parts = day_part.strip().split()
        if len(day_parts) != 2:
            return None
        
        day_str, month_str = day_parts[0], day_parts[1]
        year_str = year_part.strip()
        
        if not year_str.isdigit() or len(year_str) != 4:
            return None
            
        try:
            day = int(day_str)
            month = month_names[month_str.lower()]
            year = int(year_str)
            
            date_obj = datetime.date(year, month, day)
            return date_obj
        except (ValueError, KeyError):
            return None
    
    def parse_day_abbr_month_year(text: str) -> datetime.date | None:
        parts = text.split()
        if len(parts) != 3:
            return None
        
        day_str, month_str, year_str = parts[0], parts[1].strip(), parts[2]
        
        if not year_str.isdigit() or len(year_str) != 4:
            return None
            
        try:
            day = int(day_str)
            month = month_abbr[month_str.lower()]
            year = int(year_str)
            
            date_obj = datetime.date(year, month, day)
            return date_obj
        except (ValueError, KeyError):
            return None
    
    # Try each format in order
    if parse_iso(text):
        return datetime.datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    
    result = parse_day_month_year_slash(text)
    if result:
        return result.strftime("%Y-%m-%d")
    
    result = parse_day_full_month_year(text)
    if result:
        return result.strftime("%Y-%m-%d")
    
    result = parse_day_abbr_month_year(text)
    if result:
        return result.strftime("%Y-%m-%d")
    
    return None
