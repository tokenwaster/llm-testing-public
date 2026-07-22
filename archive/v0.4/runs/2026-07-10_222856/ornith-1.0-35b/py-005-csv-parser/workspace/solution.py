def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180-style rules."""
    if not text:
        return []
    
    records = []
    current_record: list[str] = []
    current_field = ""
    in_quotes = False      # True when inside a quoted field
    after_quote = False    # True after seeing a closing quote
    
    i = 0
    n = len(text)
    
    while i < n:
        c = text[i]
        
        if after_quote:
            # After a closing quote, next char must be comma, newline, or EOF
            if c == ',':
                current_record.append(current_field)
                current_field = ""
                after_quote = False
                i += 1
            elif c == '\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                after_quote = False
                i += 1
            elif c == '\r':
                # Handle \r\n or bare \r (treat bare \r as newline for robustness)
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    after_quote = False
                    i += 2
                else:
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    after_quote = False
                    i += 1
            else:
                raise ValueError(f"Invalid character {c!r} after closing quote")
        
        elif in_quotes:
            if c == '"':
                # Check for escaped quote (doubled)
                if i + 1 < n and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                else:
                    # Closing quote
                    in_quotes = False
                    after_quote = True
                    i += 1
            else:
                current_field += c
                i += 1
        
        else:
            # Normal (unquoted) field processing
            if c == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif c == '\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                i += 1
            elif c == '\r':
                # Handle \r\n or bare \r
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 2
                else:
                    # Bare \r treated as newline for robustness
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1
            elif c == '"' and not current_field:
                # Quote at start of field begins quoted mode
                in_quotes = True
                i += 1
            else:
                current_field += c
                i += 1
    
    # Check for unclosed quote
    if in_quotes:
        raise ValueError("Unclosed quote in CSV input")
    
    # Finalize any remaining field/record (handles EOF after closing quote, or trailing data)
    if after_quote or current_field or current_record:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
