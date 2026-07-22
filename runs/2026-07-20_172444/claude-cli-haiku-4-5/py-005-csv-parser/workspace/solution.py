def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    i = 0
    last_was_comma = False
    
    def skip_newline():
        nonlocal i
        if i < len(text) and text[i] == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
            i += 2
        elif i < len(text) and text[i] in '\r\n':
            i += 1
    
    def parse_field():
        nonlocal i
        if i >= len(text):
            return ''
        
        if text[i] == '"':
            field = []
            i += 1
            while i < len(text):
                if text[i] == '"':
                    if i + 1 < len(text) and text[i + 1] == '"':
                        field.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    field.append(text[i])
                    i += 1
            else:
                raise ValueError("Unclosed quoted field")
            return ''.join(field)
        else:
            field = []
            while i < len(text) and text[i] not in ',\n\r':
                field.append(text[i])
                i += 1
            return ''.join(field)
    
    while i < len(text) or last_was_comma:
        if i >= len(text):
            current_record.append('')
            break
        
        field = parse_field()
        current_record.append(field)
        last_was_comma = False
        
        if i >= len(text):
            break
        elif text[i] == ',':
            last_was_comma = True
            i += 1
        elif text[i] in '\r\n':
            records.append(current_record)
            current_record = []
            skip_newline()
        else:
            raise ValueError(f"Unexpected character after closing quote: {text[i]}")
    
    if current_record:
        records.append(current_record)
    
    return records
