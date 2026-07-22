def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    
    state = 'FIELD_START'
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if state == 'FIELD_START':
            if char == '"':
                state = 'IN_QUOTED'
                i += 1
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
            elif char == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
            else:
                current_field.append(char)
                state = 'IN_UNQUOTED'
                i += 1
                
        elif state == 'IN_UNQUOTED':
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'FIELD_START'
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'FIELD_START'
                i += 1
            elif char == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'FIELD_START'
                i += 1
            else:
                current_field.append(char)
                i += 1
                
        elif state == 'IN_QUOTED':
            if char == '"':
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    state = 'AFTER_QUOTE'
                    i += 1
            else:
                current_field.append(char)
                i += 1
                
        elif state == 'AFTER_QUOTE':
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'FIELD_START'
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'FIELD_START'
                i += 1
            elif char == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'FIELD_START'
                i += 1
            else:
                raise ValueError("Invalid character after closing quote")
                
    if state == 'IN_QUOTED':
        raise ValueError("Unterminated quoted field")
        
    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
