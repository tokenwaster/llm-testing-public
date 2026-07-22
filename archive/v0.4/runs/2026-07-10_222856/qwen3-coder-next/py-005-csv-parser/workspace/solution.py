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
                        if next_char not in [',', '\n', '\r']:
                            raise ValueError("Invalid character after closing quote")
                        
                        # Handle \r\n case
                        if next_char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                            i += 2
                        elif next_char in ['\n', '\r']:
                            i += 1
                        
                    current_record.append(current_field)
                    current_field = ""
                    
                    # If we hit a comma, continue to next field (empty or not)
                    if i < len(text) and text[i-1] != ',':
                        # We already consumed the separator
                        pass
                    
                    # Check if we need to continue with more fields in this record
                    while i < len(text):
                        c = text[i]
                        if c == ',':
                            current_record.append("")
                            i += 1
                        elif c == '\n':
                            records.append(current_record)
                            current_record = []
                            i += 1
                            # Handle \r\n
                            if i < len(text) and text[i] == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                                i += 2
                            elif i < len(text) and text[i] in ['\n', '\r']:
                                i += 1
                            break
                        elif c == '\r':
                            records.append(current_record)
                            current_record = []
                            i += 1
                            # Handle \r\n case
                            if i < len(text) and text[i] == '\n':
                                i += 1
                            break
                        else:
                            raise ValueError("Invalid character after closing quote")
                    continue
            
            else:
                current_field += char
                i += 1
        else:
            # Not in quotes
            if char == '"':
                # Start of quoted field - only valid at beginning of field
                if len(current_field) > 0:
                    raise ValueError("Quote in middle of field")
                in_quotes = True
                i += 1
            elif char == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\n':
                # Handle \r\n case first
                if len(current_record) > 0 or len(current_field) > 0:
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                else:
                    # Empty line creates a record with one empty field
                    records.append([""])
                
                i += 1
            elif char == '\r':
                # Check if next char is \n (handle \r\n)
                if i + 1 < len(text) and text[i + 1] == '\n':
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 2
                else:
                    # Standalone \r - treat as newline
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1
            else:
                current_field += char
                i += 1
    
    # Handle remaining data after loop ends
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field if we have one
    if len(current_field) > 0 or len(current_record) > 0:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
