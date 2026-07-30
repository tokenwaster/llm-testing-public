def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        record = []
        current_field_chars = []
        in_quotes = False
        
        while True:
            if i >= n:
                break
            
            ch = text[i]
            
            if in_quotes:
                if ch == '"':
                    # Could be doubled quote (literal) or closing quote
                    if i + 1 < n and text[i + 1] == '"':
                        current_field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote - validate next character(s)
                        in_quotes = False
                        i += 1
                        
                        if i >= n:
                            break  # EOF after closing quote, end of record
                        elif text[i] == ',':
                            pass  # Continue to next field
                        elif text[i] == '\n':
                            break  # End of record (outer handles advancing)
                        elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                            i += 2  # Skip past \r\n
                            break  # End of record, already advanced
                        else:
                            raise ValueError(
                                f"Invalid character after closing quote at position {i - 1}")
                elif ch == '\r' or ch == '\n':
                    if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                        current_field_chars.append('\r')
                        current_field_chars.append('\n')
                        i += 2
                    else:
                        current_field_chars.append(ch)
                        i += 1
                else:
                    current_field_chars.append(ch)
                    i += 1
            elif ch == ',':
                record.append("".join(current_field_chars))
                current_field_chars = []
                i += 1
            elif ch == '\r':
                # Check for \r\n; if so, treat as end of record
                if i + 1 < n and text[i + 1] == '\n':
                    break  # End of record (outer handles \r\n)
                else:
                    current_field_chars.append(ch)
                    i += 1
            elif ch == '\n':
                break  # End of record (outer handles \n)
            else:
                if ch == '"':
                    in_quotes = True
                    i += 1
                else:
                    current_field_chars.append(ch)
                    i += 1
        
        # Add last field of the record
        record.append("".join(current_field_chars))
        
        # Check for unclosed quote (only possible if we hit EOF while in quotes)
        if in_quotes:
            raise ValueError("Unclosed quote")
        
        # Handle trailing newline(s) at end of record
        if i < n and text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
            i += 2
        elif i < n and text[i] == '\n':
            i += 1
    
    return result
