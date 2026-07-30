def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
        
    records = []
    current_record = []
    current_field = []
    state = 'NORMAL'
    
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if state == 'NORMAL':
            if char == '"':
                if not current_field:
                    state = 'QUOTED'
                else:
                    current_field.append(char)
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
            elif char in ('\n', '\r'):
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'NORMAL'
            else:
                current_field.append(char)
                
        elif state == 'QUOTED':
            if char == '"':
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 1
                else:
                    state = 'AFTER_QUOTE'
            else:
                current_field.append(char)
                
        elif state == 'AFTER_QUOTE':
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'NORMAL'
            elif char in ('\n', '\r'):
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'NORMAL'
            else:
                raise ValueError("Invalid character after closing quote")
                
        i += 1
        
    if state == 'QUOTED':
        raise ValueError("Unclosed quote")
        
    if current_record or current_field or state == 'AFTER_QUOTE':
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
