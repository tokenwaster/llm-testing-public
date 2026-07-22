def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
        
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if in_quotes:
            if char == '"':
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    i += 1
                    if i < n:
                        next_char = text[i]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Invalid character after closing quote")
                    continue
            else:
                current_field.append(char)
                i += 1
        else:
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
            elif char == '\n':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
            elif char == '"':
                if current_field:
                    current_field.append(char)
                    i += 1
                else:
                    in_quotes = True
                    i += 1
            else:
                current_field.append(char)
                i += 1
                
    if in_quotes:
        raise ValueError("Unclosed quote")
        
    if current_record:
        records.append(current_record)
        
    return records
