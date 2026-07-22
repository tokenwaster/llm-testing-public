def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC 4180 rules, from scratch."""
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Handle field and record separators first
        if char == ',':
            current_record.append(current_field)
            current_field = ""
            i += 1
            continue
        
        if char in '\r\n':
            if char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # \r\n line ending
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 2
            else:
                # Single \r or \n line ending
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            continue
        
        # At the start of a new field (no characters accumulated yet)
        if not current_field:
            if char == '"':
                # Start a quoted field
                i += 1
                in_quote = True
                while i < len(text):
                    c = text[i]
                    if c == '"':
                        # Check for escaped quote (doubled)
                        if i + 1 < len(text) and text[i + 1] == '"':
                            current_field += '"'
                            i += 2
                        else:
                            # End of quoted field
                            in_quote = False
                            i += 1
                            break
                    elif c in '\r\n':
                        # Newline inside quoted field is part of the field content
                        if c == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                            current_field += '\r\n'
                            i += 2
                        else:
                            current_field += c
                            i += 1
                    else:
                        current_field += c
                        i += 1
                
                if in_quote:
                    raise ValueError("Unclosed quote in CSV field")
                
                # After closing quote, the next char must be separator or EOF
                if i < len(text) and text[i] not in ',\r\n':
                    raise ValueError(f"Invalid character after closing quote: {text[i]!r}")
            else:
                # Regular (unquoted) field character
                current_field += char
                i += 1
        else:
            # Regular character in an unquoted field
            current_field += char
            i += 1
    
    # Handle the last record/field if text doesn't end with a newline
    if current_field or current_record:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
