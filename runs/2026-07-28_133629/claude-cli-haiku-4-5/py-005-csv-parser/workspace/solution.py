def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    if text.endswith('\r\n'):
        text = text[:-2]
    elif text.endswith('\n'):
        text = text[:-1]
    
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    field_closed = False
    just_added_record = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            just_added_record = False
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    field_closed = True
                    i += 1
                    continue
            else:
                current_field.append(char)
                i += 1
        else:
            if field_closed:
                if char == ',':
                    current_record.append(''.join(current_field))
                    current_field = []
                    field_closed = False
                    just_added_record = False
                    i += 1
                elif char == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    field_closed = False
                    records.append(current_record)
                    current_record = []
                    just_added_record = True
                    i += 1
                elif char == '\r':
                    if i + 1 < len(text) and text[i + 1] == '\n':
                        current_record.append(''.join(current_field))
                        current_field = []
                        field_closed = False
                        records.append(current_record)
                        current_record = []
                        just_added_record = True
                        i += 2
                    else:
                        current_record.append(''.join(current_field))
                        current_field = []
                        field_closed = False
                        records.append(current_record)
                        current_record = []
                        just_added_record = True
                        i += 1
                else:
                    raise ValueError("Characters after closing quote")
            elif char == '"':
                if current_field:
                    raise ValueError("Unexpected quote in field")
                in_quotes = True
                just_added_record = False
                i += 1
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                just_added_record = False
                i += 1
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                just_added_record = True
                i += 1
            elif char == '\r':
                if i + 1 < len(text) and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    just_added_record = True
                    i += 2
                else:
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    just_added_record = True
                    i += 1
            else:
                current_field.append(char)
                just_added_record = False
                i += 1
    
    if in_quotes:
        raise ValueError("Unclosed quote in field")
    
    if not just_added_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
