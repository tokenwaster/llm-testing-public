def parse_csv(text: str) -> list[list[str]]:
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
                else:
                    in_quotes = False
                    if i + 1 < n:
                        next_char = text[i+1]
                        if next_char == ',':
                            current_record.append(''.join(current_field))
                            current_field = []
                            i += 1
                        elif next_char == '\n':
                            current_record.append(''.join(current_field))
                            current_field = []
                            records.append(current_record)
                            current_record = []
                            i += 1
                        elif next_char == '\r':
                            if i + 2 < n and text[i+2] == '\n':
                                current_record.append(''.join(current_field))
                                current_field = []
                                records.append(current_record)
                                current_record = []
                                i += 2
                            else:
                                raise ValueError("Invalid char after closing quote")
                        else:
                            raise ValueError("Invalid char after closing quote")
                    else:
                        current_record.append(''.join(current_field))
                        current_field = []
                        i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                in_quotes = True
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
                if i + 1 < n and text[i+1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 1
            else:
                current_field.append(char)
                i += 1
                
    if in_quotes:
        raise ValueError("Unclosed quote")
        
    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
