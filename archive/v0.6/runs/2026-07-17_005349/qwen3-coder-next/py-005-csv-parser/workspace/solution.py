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
                else:
                    # Closing quote - end of quoted field
                    in_quotes = False
                    i += 1
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                # Opening quote - start of quoted field
                in_quotes = True
                i += 1
            elif char == ',':
                # End of field
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # CRLF - end of record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 2
            elif char == '\n' or char == '\r':
                # LF or standalone CR - end of record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            else:
                current_field += char
                i += 1
    
    # Handle the last field if we're not at a record boundary
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field to the current record
    if current_field or current_record:  # If there's content or we've started a record
        current_record.append(current_field)
        records.append(current_record)
    
    # Remove trailing empty record if input ended with newline(s)
    # But only if the last record is truly empty (single empty field from trailing newline)
    if len(records) > 0:
        last_record = records[-1]
        # If the last record has exactly one field that's empty and we had a trailing newline
        # We need to check if this was caused by a trailing newline
        # Actually, let's reconsider: we should only have an extra record if there was an empty line at the end
        
        # Better approach: process input more carefully during parsing
    
    return records
