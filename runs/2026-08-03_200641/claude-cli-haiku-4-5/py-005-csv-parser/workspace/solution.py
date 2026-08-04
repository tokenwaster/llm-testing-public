def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    in_quotes = False
                    i += 1
                    if i >= len(text):
                        break
                    
                    next_char = text[i]
                    if next_char == ',':
                        current_record.append(current_field)
                        current_field = ""
                        i += 1
                    elif next_char == '\n':
                        current_record.append(current_field)
                        current_field = ""
                        records.append(current_record)
                        current_record = []
                        i += 1
                    elif next_char == '\r':
                        current_record.append(current_field)
                        current_field = ""
                        i += 1
                        if i < len(text) and text[i] == '\n':
                            i += 1
                        records.append(current_record)
                        current_record = []
                    else:
                        raise ValueError("Unexpected character after closing quote")
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                if len(current_field) == 0:
                    in_quotes = True
                else:
                    current_field += char
                i += 1
            elif char == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\n':
                current_record.append(current_field)
                current_field = ""
                records.append(current_record)
                current_record = []
                i += 1
            elif char == '\r':
                current_record.append(current_field)
                current_field = ""
                i += 1
                if i < len(text) and text[i] == '\n':
                    i += 1
                records.append(current_record)
                current_record = []
            else:
                current_field += char
                i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quote in CSV")
    
    if current_field or current_record or not records:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
