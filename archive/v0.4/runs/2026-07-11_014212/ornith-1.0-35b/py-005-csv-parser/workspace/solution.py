def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180 rules (from scratch)."""
    if not text:
        return []
    
    records = []
    current_record = []  # List of field strings for the current record
    current_field = []   # Characters being accumulated for the current field
    i = 0
    in_quotes = False
    just_closed_quote = False
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            # Inside a quoted field - most characters are literal
            if char == '"':
                # Check for escaped quote (doubled)
                if i + 1 < len(text) and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    just_closed_quote = True
                    i += 1
            elif char == '\n' or (char == '\r' and i + 1 < len(text) and text[i+1] == '\n'):
                # Newlines are allowed inside quotes
                if char == '\r':
                    current_field.append('\r\n')
                    i += 2
                else:
                    current_field.append(char)
                    i += 1
            else:
                current_field.append(char)
                i += 1
        else:
            # Not inside quotes - check for structural characters
            
            # Validate character after closing quote
            if just_closed_quote:
                if char == ',':
                    just_closed_quote = False
                elif char == '\n':
                    just_closed_quote = False
                elif char == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                    just_closed_quote = False
                else:
                    raise ValueError(f"Invalid character after closing quote: {char!r}")
            
            if char == '"' and not current_field:
                # Quote at start of field begins quoted mode
                in_quotes = True
                i += 1
            elif char == ',':
                # Field separator - finalize current field
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                # Record separator (LF)
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
            elif char == '\r' and i + 1 < len(text) and text[i+1] == '\n':
                # Record separator (CRLF)
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 2
            else:
                # Regular character - add to current field
                current_field.append(char)
                i += 1
    
    # Validate unclosed quotes
    if in_quotes:
        raise ValueError("Unclosed quote at end of input")
    
    # Finalize any remaining data (no trailing newline)
    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
    
    return records
