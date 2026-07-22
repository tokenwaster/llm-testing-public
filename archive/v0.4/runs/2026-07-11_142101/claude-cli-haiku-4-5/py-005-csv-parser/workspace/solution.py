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
                        current_record.append(current_field)
                        current_field = ""
                        records.append(current_record)
                        current_record = []
                    elif text[i] == ',':
                        current_record.append(current_field)
                        current_field = ""
                        i += 1
                    elif text[i] == '\n':
                        current_record.append(current_field)
                        current_field = ""
                        records.append(current_record)
                        current_record = []
                        i += 1
                    elif text[i] == '\r':
                        current_record.append(current_field)
                        current_field = ""
                        if i + 1 < len(text) and text[i + 1] == '\n':
                            i += 2
                        else:
                            i += 1
                        records.append(current_record)
                        current_record = []
                    else:
                        raise ValueError("Invalid character after closing quote")
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                if current_field == "":
                    in_quotes = True
                    i += 1
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
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                records.append(current_record)
                current_record = []
            else:
                current_field += char
                i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    if current_field or current_record:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
