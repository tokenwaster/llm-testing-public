def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if not in_quotes:
            if char == '"':
                # Start of a quoted field - only valid at the beginning
                in_quotes = True
                i += 1
            elif char == ',':
                # End of current field, add to record
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\n':
                # End of record (handle \r\n case first if needed)
                # Check for \r before \n
                if len(current_record) > 0 or current_field != "":
                    current_record.append(current_field)
                    records.append(current_record)
                elif current_field == "" and not current_record:
                    # Empty line creates a record with one empty field
                    records.append([""])
                else:
                    current_record.append(current_field)
                    records.append(current_record)
                
                current_record = []
                current_field = ""
                i += 1
            elif char == '\r':
                # Check if next char is \n (CRLF)
                if i + 1 < len(text) and text[i + 1] == '\n':
                    # CRLF - end of record
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 2  # Skip both \r and \n
                else:
                    # Just \r, treat as newline
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1
            else:
                # Regular character, add to field
                current_field += char
                i += 1
        else:  # in_quotes == True
            if char == '"':
                # Check if this is a doubled quote ("" -> ")
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Escaped quote, add single quote to field
                    current_field += '"'
                    i += 2  # Skip both quotes
                else:
                    # End of quoted section - check what comes next
                    in_quotes = False
                    i += 1
                    # After closing quote, we expect comma, newline, or EOF
                    if i < len(text):
                        next_char = text[i]
                        if next_char not in [',', '\n', '\r']:
                            raise ValueError(f"Invalid character after closing quote: '{next_char}'")
            else:
                # Regular character inside quotes
                current_field += char
                i += 1
    
    # Handle end of input
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field and record if needed
    if len(current_record) > 0 or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    elif current_field == "" and not current_record:
        # If we have an empty line at the end, it creates a record with one empty field
        # But only if there was actually content that ended with a newline
        # Actually, per spec: trailing newline doesn't create extra record
        # So this case shouldn't happen for valid input ending with newline
        pass
    
    return records
