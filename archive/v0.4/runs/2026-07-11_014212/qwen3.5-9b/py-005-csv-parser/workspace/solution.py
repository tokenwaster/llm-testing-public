def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    # Normalize line endings to \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        # Skip empty lines at the start (but not in middle - those create records)
        if text[i] == '\n':
            i += 1
            continue
        
        record = []
        field_start = i
        
        while i < n:
            c = text[i]
            
            if c == '"':
                # Start of quoted field (or continuation)
                j = i + 1
                
                # Parse until closing quote
                while j < n:
                    if text[j] == '"':
                        # Check for escaped quote
                        if j + 1 < n and text[j + 1] == '"':
                            # Escaped quote - add single quote to field
                            record.append('"')
                            i = j + 2
                            continue
                        else:
                            # End of quoted section
                            break
                    else:
                        record.append(text[j])
                        i = j + 1
                
                # After closing quote, check what comes next
                if i < n:
                    next_c = text[i]
                    if next_c == ',':
                        i += 1
                    elif next_c == '\n':
                        break
                    else:
                        raise ValueError("Malformed CSV: characters after closing quote")
            elif c == ',':
                # End of field, add it and start new field
                record.append(text[field_start:i])
                field_start = i + 1
                i += 1
            elif c == '\n':
                # End of record (only if not inside quotes - handled above)
                break
            else:
                i += 1
        
        # Add the last field in the record
        if field_start < i:
            record.append(text[field_start:i])
        
        result.append(record)
    
    return result
