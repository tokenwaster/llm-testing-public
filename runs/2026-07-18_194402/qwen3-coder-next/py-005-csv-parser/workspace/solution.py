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
                # Start of a quoted field
                in_quotes = True
            elif char == ',':
                # End of current field, add to record
                current_record.append(current_field)
                current_field = ""
            elif char == '\n':
                # End of record (handle \r\n case first if needed)
                # Check if previous character was \r
                if len(current_record) > 0 or current_field != "":
                    current_record.append(current_field)
                    records.append(current_record)
                else:
                    # Empty line creates a record with one empty field
                    records.append([""])
                current_record = []
                current_field = ""
            elif char == '\r':
                # Check if next character is \n (CRLF)
                if i + 1 < len(text) and text[i+1] == '\n':
                    # CRLF - end of record
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1  # Skip the \n
                else:
                    # Just \r, treat as newline
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
            else:
                # Regular character, add to field
                current_field += char
        else:  # in_quotes is True
            if char == '"':
                # Check if this is a doubled quote ("" -> ")
                if i + 1 < len(text) and text[i+1] == '"':
                    # Escaped quote, add single quote to field
                    current_field += '"'
                    i += 1  # Skip the next quote
                else:
                    # End of quoted section
                    in_quotes = False
            else:
                # Regular character inside quotes
                current_field += char
        
        i += 1
    
    # Handle last record if there's no trailing newline
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Process the last field/record
    if len(current_record) > 0 or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    elif text and (text[-1] == '\n' or text[-1] == '\r'):
        # If text ends with newline, we might have an empty record at the end
        # But per spec, trailing newline doesn't create extra record
        pass
    
    return records
