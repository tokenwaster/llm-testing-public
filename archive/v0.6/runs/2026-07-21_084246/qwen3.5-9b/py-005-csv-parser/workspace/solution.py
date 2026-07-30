def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    
    i = 0
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check for escaped quote ("" -> ")
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    current_record.append(''.join(current_field))
                    current_field = []
            else:
                current_field.append(char)
        else:
            if char == '"':
                # Starting a quoted field
                in_quotes = True
                current_field.append(char)
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
            elif char == '\n':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
                continue
            elif char == '\r':
                # Handle \r\n or standalone \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    i += 2
                    continue
                else:
                    # Standalone \r treated as newline
                    current_record.append(''.join(current_field))
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    i += 1
                    continue
            else:
                current_field.append(char)
        
        i += 1
    
    # Handle last field if not empty (but only if we're not in quotes at EOF)
    if current_field and not in_quotes:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
