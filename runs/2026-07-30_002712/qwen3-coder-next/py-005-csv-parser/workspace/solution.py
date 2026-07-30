def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(text):
        c = text[i]
        
        if not in_quotes:
            if c == '"':
                # Start of a quoted field - only valid at the beginning
                in_quotes = True
            elif c == ',':
                # End of field, add to current record
                current_record.append(current_field)
                current_field = ""
            elif c == '\n':
                # End of record (but not at start of empty line)
                if current_field != "" or len(current_record) > 0:
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                else:
                    # This handles the case where we have an empty line
                    # which should be a record with one empty field
                    if i > 0 and text[i-1] != '\r' or i == 0:
                        if len(current_record) == 0:  # Empty line, add empty record
                            current_record.append("")
                            records.append(current_record)
                            current_record = []
                        else:
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            current_field = ""
                    else:
                        current_record.append(current_field)
                        records.append(current_record)
                        current_record = []
                        current_field = ""
            elif c == '\r':
                # Check for \r\n
                if i + 1 < len(text) and text[i+1] == '\n':
                    i += 1  # Skip the \n as well
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                else:
                    # Just \r (old Mac style), treat as record separator
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
            else:
                current_field += c
        else:  # in_quotes is True
            if c == '"':
                # Check for escaped quote (doubled)
                if i + 1 < len(text) and text[i+1] == '"':
                    # Escaped quote, add single quote
                    current_field += '"'
                    i += 1  # Skip the next quote
                else:
                    # End of quoted section - check what comes next
                    # If nothing (EOF), field is done, but we need to end record properly
                    if i + 1 >= len(text):
                        # End of input after closing quote
                        current_record.append(current_field)
                        records.append(current_record)
                        return records
                    elif text[i+1] == ',':
                        # Field ends with comma - valid
                        current_record.append(current_field)
                        current_field = ""
                        in_quotes = False
                        i += 1
                    elif text[i+1] == '\n':
                        # Field ends with newline - valid
                        current_record.append(current_field)
                        records.append(current_record)
                        current_record = []
                        current_field = ""
                        in_quotes = False
                        if i + 1 < len(text) and text[i+1] == '\r':
                            # Handle \r\n case in quoted field ending
                            i += 1
                        i += 1
                        continue
                    elif text[i+1] == '\r':
                        # Check for \r\n at end of field
                        if i + 2 < len(text) and text[i+2] == '\n':
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            current_field = ""
                            in_quotes = False
                            i += 2  # Skip \r\n
                        else:
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            current_field = ""
                            in_quotes = False
                            i += 1
                        continue
                    else:
                        # Invalid character after closing quote (not comma, newline or EOF)
                        raise ValueError("Invalid characters after quoted field")
            else:
                current_field += c
        
        i += 1
    
    # Handle remaining data - check if there's a final record to add
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    if len(current_record) > 0 or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
