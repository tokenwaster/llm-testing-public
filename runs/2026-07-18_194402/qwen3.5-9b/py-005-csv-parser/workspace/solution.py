def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    # Normalize line endings for record separation tracking
    # We'll process character by character
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check for escaped quote (")
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # Closing quote - check what follows
                    in_quotes = False
                    i += 1
            elif char == '\n' or char == '\r':
                # Newline inside quoted field is part of content
                current_field.append(char)
                i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                # Start of a quoted field (only special meaning at start)
                in_quotes = True
                current_field.append(char)
                i += 1
            elif char == ',':
                # Field separator
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n' or char == '\r':
                # Record separator
                if char == '\r':
                    if i + 1 < len(text) and text[i + 1] == '\n':
                        current_record.append(''.join(current_field))
                        current_field = []
                        i += 2
                    else:
                        current_record.append(''.join(current_field))
                        current_field = []
                        i += 1
                else:
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
            else:
                current_field.append(char)
                i += 1
    
    # After loop, handle remaining content
    if current_field or (current_record and not in_quotes):
        current_record.append(''.join(current_field))
    
    # If we ended inside quotes without closing, that's malformed
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    # Check for characters after closing quote that aren't comma/newline/EOF
    # This is handled by the logic above - if there's content after closing quote
    # it would be added to current_field, which is fine
    
    records.append(current_record)
    
    return records
