def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            # We're inside a quoted field
            if char == '"':
                # Check if it's a doubled quote or the closing quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Doubled quote: add one quote to the field
                    current_field.append('"')
                    i += 2
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
                    # After closing quote, we must see comma, newline, or EOF
                    if i < len(text):
                        if text[i] == ',':
                            # Comma after closing quote: field ends
                            current_record.append(''.join(current_field))
                            current_field = []
                            i += 1
                        elif text[i] == '\n':
                            # Newline after closing quote: record ends
                            current_record.append(''.join(current_field))
                            current_field = []
                            records.append(current_record)
                            current_record = []
                            i += 1
                        elif text[i] == '\r':
                            # Could be \r\n
                            current_record.append(''.join(current_field))
                            current_field = []
                            if i + 1 < len(text) and text[i + 1] == '\n':
                                i += 2
                            else:
                                i += 1
                            records.append(current_record)
                            current_record = []
                        else:
                            # Invalid: character after closing quote that isn't comma/newline
                            raise ValueError("Characters after closing quote must be comma or newline")
            else:
                # Regular character inside quoted field
                current_field.append(char)
                i += 1
        else:
            # We're outside a quoted field
            if char == '"':
                # Opening quote: field must start with quote for quotes to be special
                if current_field or current_record:
                    # Quote doesn't start the field, treat as literal
                    current_field.append(char)
                    i += 1
                else:
                    # Quote starts the field
                    in_quotes = True
                    i += 1
            elif char == ',':
                # Field separator
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                # Record separator
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif char == '\r':
                # Could be \r or \r\n
                current_record.append(''.join(current_field))
                current_field = []
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                records.append(current_record)
                current_record = []
            else:
                # Regular character
                current_field.append(char)
                i += 1
    
    # Handle any remaining field/record
    if in_quotes:
        # Unclosed quote
        raise ValueError("Unclosed quote in CSV")
    
    # Add the last field and record if there's anything
    current_record.append(''.join(current_field))
    if current_record != [''] or records:  # Only add if non-empty or if we have previous records
        if current_record or records:
            records.append(current_record)
    
    # Remove trailing empty record if input ends with newline
    if records and records[-1] == ['']:
        if len(text) > 0 and text[-1] in '\n\r':
            records.pop()
    
    return records
