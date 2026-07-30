def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    in_quotes = False
    last_was_newline = False
    
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
                            raise ValueError("Invalid characters after closing quote")
                    continue
            else:
                current_field.append(char)
                i += 1
                last_was_newline = False
                continue
        else:
            if char == '"' and len(current_field) == 0:
                in_quotes = True
                i += 1
                continue
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
                continue
            elif char == '\n' or char == '\r':
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                last_was_newline = True
                continue
            else:
                current_field.append(char)
                i += 1
                last_was_newline = False
                continue
                
    if in_quotes:
        raise ValueError("Unclosed quote")
        
    if not last_was_newline:
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
