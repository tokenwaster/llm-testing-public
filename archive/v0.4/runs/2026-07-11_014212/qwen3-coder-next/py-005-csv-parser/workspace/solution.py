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
                # Check if it's a doubled quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2  # Skip both quotes
                    continue
                else:
                    # End of quoted field - check what comes next
                    in_quotes = False
                    i += 1
                    
                    # After closing quote, we should have comma, newline, or EOF
                    if i < len(text):
                        next_char = text[i]
                        if next_char == ',':
                            # Valid: end of field, continue to next field
                            current_record.append(current_field)
                            current_field = ""
                            i += 1
                            continue
                        elif next_char in '\r\n':
                            # Valid: end of record
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            current_field = ""
                            
                            # Handle \r\n
                            if next_char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                                i += 2
                            else:
                                i += 1
                            continue
                        else:
                            # Invalid: characters after closing quote that aren't comma/newline/EOF
                            raise ValueError(f"Invalid character(s) after quoted field at position {i}")
                    else:
                        # EOF after closing quote - valid, end of record
                        current_record.append(current_field)
                        records.append(current_record)
                        current_record = []
                        current_field = ""
                        break
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                # Start of quoted field (only if it's the first character of a field)
                in_quotes = True
                i += 1
            elif char == ',':
                # End of field
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\r':
                # Handle \r\n or standalone \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    # \r\n - end of record
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 2  # Skip both characters
                else:
                    # Standalone \r - end of record
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1
            elif char == '\n':
                # End of record (standalone \n)
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += char
                i += 1
    
    # After processing all characters, check if we have a pending record
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # If we have fields in the current record (not yet added)
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
