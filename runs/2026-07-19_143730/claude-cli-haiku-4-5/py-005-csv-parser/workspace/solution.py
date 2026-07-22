def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    last_was_line_terminator = False
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check if it's a doubled quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    # After closing quote, next char must be comma, newline, or EOF
                    if i < len(text) and text[i] not in (',', '\r', '\n'):
                        raise ValueError("Unexpected character after closing quote")
                    continue
            else:
                current_field.append(char)
                i += 1
        else:
            if char == '"':
                # Quote is special only at start of field
                if len(current_field) == 0:
                    in_quotes = True
                else:
                    # Literal quote character
                    current_field.append('"')
                i += 1
            elif char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
                last_was_line_terminator = False
            elif char == '\r':
                current_record.append(''.join(current_field))
                current_field = []
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                records.append(current_record)
                current_record = []
                last_was_line_terminator = True
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
                records.append(current_record)
                current_record = []
                last_was_line_terminator = True
            else:
                current_field.append(char)
                i += 1
                last_was_line_terminator = False
    
    # End of input
    if in_quotes:
        raise ValueError("Unclosed quote")
    
    # Add the final field and record (unless it's just an artifact of trailing newline)
    current_record.append(''.join(current_field))
    if not (last_was_line_terminator and current_record == ['']):
        records.append(current_record)
    
    return records
