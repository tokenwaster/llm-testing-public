def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180-style rules."""
    if not text:
        return []
    
    result = []
    current_record = []
    current_field = ""
    i = 0
    n = len(text)
    in_quotes = False
    
    while i < n:
        c = text[i]
        
        if in_quotes:
            # Inside a quoted field
            if c == '"':
                # Check for escaped quote (doubled)
                if i + 1 < n and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    # Closing quote — must be followed by comma, newline, or EOF
                    in_quotes = False
                    i += 1
                    if i < n and text[i] not in (',', '\n', '\r'):
                        raise ValueError(
                            f"Invalid character after closing quote: '{text[i]}'"
                        )
            elif c == '\r' or c == '\n':
                # Newline inside quotes is part of the field content
                if c == '\r' and i + 1 < n and text[i + 1] == '\n':
                    current_field += '\r\n'
                    i += 2
                else:
                    current_field += c
                    i += 1
            else:
                current_field += c
                i += 1
        else:
            # Outside quotes — normal field processing
            if c == '"':
                # Opening quote starts a quoted field
                in_quotes = True
                i += 1
            elif c == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif c == '\n':
                # Record separator: bare \n
                current_record.append(current_field)
                result.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                # Record separator: \r\n
                current_record.append(current_field)
                result.append(current_record)
                current_record = []
                current_field = ""
                i += 2
            elif c == '\r':
                # Bare \r is not a record separator per spec; treat as field data
                current_field += c
                i += 1
            else:
                current_field += c
                i += 1
    
    # If we ended while still inside quotes, the input was malformed
    if in_quotes:
        raise ValueError("Unclosed quote — opening quote never terminated")
    
    # Append any remaining field/record (handles missing trailing newline)
    if current_record or current_field:
        current_record.append(current_field)
        result.append(current_record)
    
    return result
