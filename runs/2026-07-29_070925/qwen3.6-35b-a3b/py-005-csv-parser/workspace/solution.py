def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    rows = []
    current_row = []
    current_field = []
    i = 0
    n = len(text)
    in_quotes = False
    
    while i < n:
        char = text[i]
        
        if in_quotes:
            if char == '"':
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote
                    if i + 1 < n:
                        next_char = text[i+1]
                        if next_char == ',':
                            current_row.append(''.join(current_field))
                            current_field = []
                            in_quotes = False
                            i += 2 
                            continue
                        elif next_char == '\n':
                            current_row.append(''.join(current_field))
                            rows.append(current_row)
                            current_row = []
                            current_field = []
                            in_quotes = False
                            i += 2 
                            continue
                        elif next_char == '\r' and i + 2 < n and text[i+2] == '\n':
                            current_row.append(''.join(current_field))
                            rows.append(current_row)
                            current_row = []
                            current_field = []
                            in_quotes = False
                            i += 3 
                            continue
                        else:
                            raise ValueError(f"Invalid character after closing quote: '{next_char}'")
                    else:
                        # EOF after closing quote
                        current_row.append(''.join(current_field))
                        rows.append(current_row)
                        current_row = []
                        current_field = []
                        in_quotes = False
                        i += 1 
                        continue
            else:
                current_field.append(char)
        else:
            if char == '"':
                if not current_field:
                    in_quotes = True
                else:
                    current_field.append(char)
            elif char == ',':
                current_row.append(''.join(current_field))
                current_field = []
            elif char == '\r' and i + 1 < n and text[i+1] == '\n':
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                i += 2
            elif char == '\n':
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
            else:
                current_field.append(char)
        i += 1
        
    if in_quotes:
        raise ValueError("Unterminated quoted field")
        
    if current_field or current_row:
        if current_field:
            current_row.append(''.join(current_field))
        rows.append(current_row)
        
    return rows
