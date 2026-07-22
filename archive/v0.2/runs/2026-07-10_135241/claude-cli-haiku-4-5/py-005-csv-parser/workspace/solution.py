def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    quote_closed = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if quote_closed:
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                quote_closed = False
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                quote_closed = False
                i += 1
            elif char == '\r':
                if i + 1 < len(text) and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    quote_closed = False
                    i += 2
                else:
                    raise ValueError(f"Invalid character after closing quote: {char}")
            else:
                raise ValueError(f"Invalid character after closing quote: {char}")
        elif in_quotes:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    in_quotes = False
                    quote_closed = True
                    i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                if not current_field:
                    in_quotes = True
                    i += 1
                else:
                    current_field.append(char)
                    i += 1
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif char == '\r':
                if i + 1 < len(text) and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    current_field.append(char)
                    i += 1
            else:
                current_field.append(char)
                i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    if quote_closed or current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
