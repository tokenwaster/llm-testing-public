def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if in_quotes:
            if char == '"':
                # Check if it's a doubled quote
                if i + 1 < len(text) and text[i + 1] == '"':
                    current_field += '"'
                    i += 2  # Skip both quotes
                    continue
                else:
                    # End of quoted field - check what comes next
                    in_quotes = False
                    i += 1
                    
                    # After closing quote, we should have comma, newline, or EOF
                    if i < len(text):
                        next_char = text[i]
                        if next_char == ',':
                            i += 1  # consume the comma
                            current_record.append(current_field)
                            current_field = ""
                        elif next_char in '\r\n':
                            # Handle \r\n and \n
                            if next_char == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                                i += 2  # consume \r\n
                            else:
                                i += 1  # consume \n or \r
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            current_field = ""
                        else:
                            # Malformed: characters after closing quote that aren't comma/newline/EOF
                            raise ValueError(f"Invalid character after quoted field at position {i}")
                    else:
                        # EOF after closing quote - end of record
                        current_record.append(current_field)
                        records.append(current_record)
                        current_record = []
                        current_field = ""
            else:
                current_field += char
                i += 1
        else:
            if char == '"':
                in_quotes = True
                i += 1
            elif char == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            elif char == '\r':
                # Check for \r\n or just \r
                if i + 1 < len(text) and text[i + 1] == '\n':
                    i += 2  # consume \r\n
                else:
                    i += 1  # consume \r
                
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            elif char == '\n':
                i += 1
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            else:
                current_field += char
                i += 1
    
    # Handle the last field if we haven't ended a record yet
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # If there's content in current_field or current_record is not empty, add it
    if current_record or current_field != "":
        current_record.append(current_field)
        records.append(current_record)
    
    return records
