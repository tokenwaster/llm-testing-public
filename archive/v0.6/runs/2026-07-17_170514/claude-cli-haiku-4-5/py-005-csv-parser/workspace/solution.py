def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    just_closed_record = False
    
    while i < len(text):
        char = text[i]
        just_closed_record = False
        
        if in_quotes:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    in_quotes = False
                    i += 1
                    if i < len(text):
                        next_char = text[i]
                        if next_char not in [',', '\n', '\r']:
                            raise ValueError("Invalid character after closing quote")
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                if len(current_field) == 0:
                    in_quotes = True
                    i += 1
                else:
                    current_field.append(char)
                    i += 1
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\r':
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                just_closed_record = True
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                just_closed_record = True
                i += 1
            else:
                current_field.append(char)
                i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    if not just_closed_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
