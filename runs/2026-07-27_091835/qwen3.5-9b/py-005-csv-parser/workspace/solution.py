def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180 style rules from scratch."""
    if not text:
        return []
    
    # Normalize line endings: \r\n and \r both become \n
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    
    result = []
    current_record = []
    current_field = []
    in_quotes = False
    
    n = len(normalized)
    i = 0
    
    while i < n:
        char = normalized[i]
        
        if char == ',':
            # Comma outside quotes ends the field
            current_record.append(''.join(current_field))
            current_field = []
            
        elif char == '\n':
            # Newline outside quotes ends the record
            current_record.append(''.join(current_field))
            current_field = []
            
            # Check if this is a trailing newline or empty line in middle
            next_idx = i + 1
            if next_idx < n:
                if normalized[next_idx] == '\n':
                    # Another newline follows - skip (empty line at end/middle)
                    pass
                else:
                    # Real content follows - finalize this record
                    result.append(current_record)
                    current_record = []
            else:
                # EOF - trailing newline, don't create empty record
        
        elif char == '"':
            if not in_quotes:
                # Start of quoted field
                in_quotes = True
            
            else:
                # Inside quotes - check for escaped quote "" or end of quoted section
                next_idx = i + 1
                if next_idx < n and normalized[next_idx] == '"':
                    # Escaped quote - decode to single "
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field - validate what follows
                    in_quotes = False
                    next_idx = i + 1
                    
                    if next_idx < n and normalized[next_idx] not in (',', '\n'):
                        raise ValueError("Malformed input")
        
        else:
            current_field.append(char)
        
        i += 1
    
    # Handle remaining content after loop
    if current_record or current_field:
        current_record.append(''.join(current_field))
    
    result.append(current_record)
    
    return result
