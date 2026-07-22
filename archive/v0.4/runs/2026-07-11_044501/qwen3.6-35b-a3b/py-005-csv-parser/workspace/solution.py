def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    # Normalize line endings to \n for uniform processing
    text = text.replace('\r\n', '\n')
    
    records = []
    i = 0
    n = len(text)
    
    while i < n:
        record = []
        while i < n:
            if text[i] == '"':
                i += 1
                field_chars = []
                while i < n:
                    if text[i] == '"':
                        if i + 1 < n and text[i+1] == '"':
                            field_chars.append('"')
                            i += 2
                        else:
                            i += 1
                            if i < n and text[i] != ',' and text[i] != '\n':
                                raise ValueError("Invalid character after closing quote")
                            break
                    else:
                        field_chars.append(text[i])
                        i += 1
                else:
                    raise ValueError("Unclosed quote")
                record.append(''.join(field_chars))
            else:
                field_chars = []
                while i < n and text[i] != ',' and text[i] != '\n':
                    field_chars.append(text[i])
                    i += 1
                record.append(''.join(field_chars))
            
            if i < n and text[i] == ',':
                i += 1
            elif i < n and text[i] == '\n':
                i += 1
                records.append(record)
                break
            else:
                records.append(record)
                break
        else:
            pass
            
    return records
