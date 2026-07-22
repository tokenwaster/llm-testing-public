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
                # Check if this is a doubled quote ("" -> ")
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                    continue
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    # After closing quote, must be comma, newline, or EOF
                    if i < len(text):
                        next_char = text[i]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Invalid character after closing quote")
                    continue
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                # Start of quoted field - only valid at beginning of field
                if current_field != "":
                    # Field already has content, so this quote is literal
                    current_field += char
                    i += 1
                else:
                    in_quotes = True
                    i += 1
            elif char == ',':
                # End of field
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\r':
                # Could be \r\n, check next char
                if i + 1 < len(text) and text[i + 1] == '\n':
                    # Record separator (\r\n)
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 2
                else:
                    # Standalone \r as record separator
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1
            elif char == '\n':
                # Record separator (\n)
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += char
                i += 1
    
    # Handle last field if not in quotes
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field to the last record
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
