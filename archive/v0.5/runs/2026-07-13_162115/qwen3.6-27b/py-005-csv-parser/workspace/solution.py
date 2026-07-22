def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    field_start = True
    after_quote = False
    i = 0
    n = len(text)
    
    while i < n:
        c = text[i]
        
        if after_quote:
            if c == ',' or c == '\n' or c == '\r':
                after_quote = False
            else:
                raise ValueError("Invalid character after closing quote")
                
        if field_start:
            if c == '"':
                in_quotes = True
                field_start = False
                i += 1
                continue
            else:
                field_start = False
                in_quotes = False
                
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    after_quote = True
                    i += 1
                    continue
            else:
                current_field.append(c)
                i += 1
                continue
                
        if c == ',':
            current_record.append(''.join(current_field))
            current_field = []
            field_start = True
            i += 1
            continue
        if c == '\r':
            if i + 1 < n and text[i+1] == '\n':
                i += 1
            current_record.append(''.join(current_field))
            records.append(current_record)
            current_record = []
            current_field = []
            field_start = True
            i += 1
            continue
        if c == '\n':
            current_record.append(''.join(current_field))
            records.append(current_record)
            current_record = []
            current_field = []
            field_start = True
            i += 1
            continue
        else:
            current_field.append(c)
            i += 1
            continue
            
    if in_quotes:
        raise ValueError("Unclosed quote")
        
    if current_record or current_field or after_quote:
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
