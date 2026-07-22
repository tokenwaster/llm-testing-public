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
            elif char == ',':
                # End of current field, add to record
                current_record.append(current_field)
                current_field = ""
            elif char == '\n':
                # End of record (handle \r\n case first if needed)
                # Check for \r before \n
                if i > 0 and text[i-1] == '\r':
                    # Already handled the \r, just end the record
                    pass
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            elif char == '\r':
                # Check if next char is \n (CRLF)
                if i + 1 < len(text) and text[i+1] == '\n':
                    # CRLF - will be handled by the \n case
                    pass
                else:
                    # Just CR as line ending
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
            else:
                # Regular character, add to field
                current_field += char
        else:  # in_quotes is True
            if char == '"':
                # Check for doubled quote or closing quote
                if i + 1 < len(text) and text[i+1] == '"':
                    # Doubled quote - add single quote
                    current_field += '"'
                    i += 1  # Skip the next quote
                else:
                    # Closing quote
                    in_quotes = False
            else:
                # Regular character inside quotes
                current_field += char
        
        i += 1
    
    # Handle last field/record if not ended by newline
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    # Check for malformed input (unclosed quotes)
    # We need to check during parsing, but since we're doing it after,
    # let's modify the approach to validate during parsing
    
    return records
