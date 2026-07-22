def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    record = []
    field = []
    state = 'FIELD'
    
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        
        if state == 'FIELD':
            if c == '"':
                state = 'QUOTED'
            elif c == ',':
                record.append(''.join(field))
                field = []
            elif c == '\n':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
            elif c == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 1
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
            else:
                field.append(c)
                
        elif state == 'QUOTED':
            if c == '"':
                if i + 1 < n and text[i+1] == '"':
                    field.append('"')
                    i += 1
                else:
                    state = 'AFTER_QUOTE'
            else:
                field.append(c)
                
        elif state == 'AFTER_QUOTE':
            if c == ',':
                record.append(''.join(field))
                field = []
                state = 'FIELD'
            elif c == '\n':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'FIELD'
            elif c == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 1
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'FIELD'
            else:
                raise ValueError("Invalid character after closing quote")
                
        i += 1
        
    if state == 'QUOTED':
        raise ValueError("Unclosed quote")
        
    record.append(''.join(field))
    if record:
        records.append(record)
        
    return records
