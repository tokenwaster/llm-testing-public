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
                # Start of a quoted field - only valid if it's the first character
                in_quotes = True
            elif char == ',':
                # End of current field, add to record
                current_record.append(current_field)
                current_field = ""
            elif char == '\n' or char == '\r':
                # Handle line endings
                # Check for \r\n
                if char == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                    i += 1
                
                # End of current record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            else:
                # Regular character, add to field
                current_field += char
        else:  # in_quotes is True
            if char == '"':
                # Check for escaped quote (doubled quote)
                if i + 1 < len(text) and text[i+1] == '"':
                    # Escaped quote - add single quote to field
                    current_field += '"'
                    i += 1  # Skip the next quote
                else:
                    # End of quoted section
                    in_quotes = False
            else:
                # Regular character inside quotes, add to field
                current_field += char
        
        i += 1
    
    # Handle case where file doesn't end with newline
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
