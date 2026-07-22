def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    result = []
    current_record = []
    current_field = ""
    i = 0
    in_quotes = False
    quote_closed = False
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    in_quotes = False
                    quote_closed = True
                    i += 1
            else:
                current_field += char
                i += 1
        else:
            if quote_closed:
                if char == ',':
                    current_record.append(current_field)
                    current_field = ""
                    quote_closed = False
                    i += 1
                elif char == '\n':
                    current_record.append(current_field)
                    current_field = ""
                    quote_closed = False
                    result.append(current_record)
                    current_record = []
                    i += 1
                elif char == '\r':
                    current_record.append(current_field)
                    current_field = ""
                    quote_closed = False
                    if i + 1 < len(text) and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    result.append(current_record)
                    current_record = []
                else:
                    raise ValueError("Unexpected character after closing quote")
            else:
                if not current_field and char == '"':
                    in_quotes = True
                    i += 1
                elif char == ',':
                    current_record.append(current_field)
                    current_field = ""
                    i += 1
                elif char == '\n':
                    current_record.append(current_field)
                    current_field = ""
                    result.append(current_record)
                    current_record = []
                    i += 1
                elif char == '\r':
                    current_record.append(current_field)
                    current_field = ""
                    if i + 1 < len(text) and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    result.append(current_record)
                    current_record = []
                else:
                    current_field += char
                    i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    if current_field or current_record:
        current_record.append(current_field)
        result.append(current_record)
    
    return result
