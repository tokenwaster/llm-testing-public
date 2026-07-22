def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180 style rules."""
    if not text:
        return []
    
    records = []
    current_record = []
    current_field = ""
    at_field_start = True
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # Check for start of quoted field (only if at the beginning of a field)
        if at_field_start and char == '"':
            at_field_start = False
            i += 1
            
            # Parse quoted field content until closing quote
            in_quotes = True
            while in_quotes:
                if i >= len(text):
                    raise ValueError("Unclosed quote")
                
                if text[i] == '"':
                    # Check for escaped quote (doubled)
                    if i + 1 < len(text) and text[i+1] == '"':
                        current_field += '"'
                        i += 2
                    else:
                        # Closing quote found
                        i += 1
                        in_quotes = False
                        
                        # Validate what follows the closing quote
                        if i >= len(text):
                            # EOF is valid after closing quote
                            pass
                        elif text[i] == ',':
                            # Next field separator
                            at_field_start = True
                            current_record.append(current_field)
                            current_field = ""
                            i += 1
                        elif text[i] == '\n' or (text[i] == '\r' and 
                              i + 1 < len(text) and text[i+1] == '\n'):
                            # Record separator (\n or \r\n)
                            if text[i] == '\r':
                                i += 2  # Skip \r\n
                            else:
                                i += 1  # Just \n
                            
                            current_record.append(current_field)
                            records.append(current_record)
                            current_record = []
                            at_field_start = True
                            current_field = ""
                        else:
                            raise ValueError(
                                "Invalid character after closing quote")
                else:
                    # Any character inside quotes is part of the field value
                    current_field += text[i]
                    i += 1
                    
        elif char == ',':
            # Field separator
            current_record.append(current_field)
            current_field = ""
            at_field_start = True
            i += 1
            
        elif char == '\n' or (char == '\r' and 
             i + 1 < len(text) and text[i+1] == '\n'):
            # Record separator (\n or \r\n only; bare \r is field content)
            if char == '\r':
                i += 2  # Skip \r\n
            else:
                i += 1  # Just \n
            
            current_record.append(current_field)
            records.append(current_record)
            current_record = []
            at_field_start = True
            current_field = ""
            
        else:
            # Regular character (not a separator, not a quote at field start)
            current_field += char
            at_field_start = False
            i += 1
    
    # Handle trailing field/record if input doesn't end with newline
    if current_field or current_record:
        current_record.append(current_field)
        records.append(current_record)
    
    return records
