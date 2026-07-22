def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field_chars = []
    i = 0
    n = len(text)
    in_quotes = False
    post_quote = False
    has_content = False
    
    while i < n:
        c = text[i]
        
        if post_quote:
            # After closing a quote, only comma or newline (or EOF) is allowed
            if c == ',':
                current_record.append(''.join(current_field_chars))
                current_field_chars = []
                has_content = False
                post_quote = False
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                # \r\n record separator
                current_record.append(''.join(current_field_chars))
                records.append(current_record)
                current_record = []
                current_field_chars = []
                has_content = False
                post_quote = False
                i += 2
            elif c == '\n':
                # \n record separator
                current_record.append(''.join(current_field_chars))
                records.append(current_record)
                current_record = []
                current_field_chars = []
                has_content = False
                post_quote = False
                i += 1
            else:
                raise ValueError("Invalid character after closing quote")
        elif in_quotes:
            if c == '"':
                # Check for escaped quote (doubled)
                if i + 1 < n and text[i + 1] == '"':
                    current_field_chars.append('"')
                    has_content = True
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    post_quote = True
                    i += 1
            else:
                current_field_chars.append(c)
                has_content = True
                i += 1
        else:
            if c == ',':
                # Field separator
                current_record.append(''.join(current_field_chars))
                current_field_chars = []
                has_content = False
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                # \r\n record separator
                current_record.append(''.join(current_field_chars))
                records.append(current_record)
                current_record = []
                current_field_chars = []
                has_content = False
                i += 2
            elif c == '\n':
                # \n record separator
                current_record.append(''.join(current_field_chars))
                records.append(current_record)
                current_record = []
                current_field_chars = []
                has_content = False
                i += 1
            elif c == '"' and not current_field_chars:
                # Start of quoted field (only valid at the beginning of a field)
                in_quotes = True
                post_quote = False
                has_content = True
                i += 1
            else:
                # Regular character in an unquoted field
                current_field_chars.append(c)
                has_content = True
                i += 1
    
    # Handle the last record/field if any
    if has_content or current_record:
        if in_quotes:
            raise ValueError("Unclosed quote")
        current_record.append(''.join(current_field_chars))
        records.append(current_record)
    
    return records
