def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    n = len(text)
    i = 0
    
    current_record = []
    current_field = []
    in_quotes = False
    field_start = True
    last_char_was_newline = False
    
    while i < n:
        char = text[i]
        if in_quotes:
            if char == '"':
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    in_quotes = False
                    i += 1
                    if i < n and text[i] not in (',', '\n', '\r'):
                        raise ValueError("Malformed CSV: character after closing quote")
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"' and field_start:
                in_quotes = True
                field_start = False
                i += 1
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                field_start = True
                i += 1
                last_char_was_newline = False
            elif char == '\n':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                field_start = True
                i += 1
                last_char_was_newline = True
            elif char == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append("".join(current_field))
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    field_start = True
                    i += 2
                    last_char_was_newline = True
                else:
                    current_field.append(char)
                    i += 1
                    field_start = False
                    last_char_was_newline = False
            else:
                current_field.append(char)
                i += 1
                field_start = False
                last_char_was_newline = False
                
    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quote")
        
    if not last_char_was_newline:
        if field_start:
            current_record.append("")
        else:
            current_record.append("".join(current_field))
        records.append(current_record)
        
    return records
