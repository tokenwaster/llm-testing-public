def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    i = 0
    
    while i < len(text):
        # Check if field starts with quote
        if text[i] == '"':
            # Quoted field
            i += 1  # skip opening quote
            field_chars = []
            closed = False
            
            while i < len(text):
                if text[i] == '"':
                    # Check next character
                    if i + 1 < len(text) and text[i + 1] == '"':
                        # Escaped quote
                        field_chars.append('"')
                        i += 2
                    else:
                        # End of quoted field
                        i += 1  # skip closing quote
                        closed = True
                        
                        # Check what follows
                        if i < len(text) and text[i] not in (',', '\n'):
                            raise ValueError(f"Invalid character after closing quote at position {i}")
                        
                        break
                else:
                    field_chars.append(text[i])
                    i += 1
            
            if not closed:
                raise ValueError("Unclosed quoted field")
            
            current_field = ''.join(field_chars)
        else:
            # Unquoted field - read until comma or newline
            field_chars = []
            while i < len(text) and text[i] not in (',', '\n'):
                field_chars.append(text[i])
                i += 1
            
            current_field = ''.join(field_chars)
        
        # Check what follows the field
        if i < len(text):
            if text[i] == ',':
                # End of field, continue to next field in same record
                current_record.append(current_field)
                i += 1  # skip comma
            elif text[i] == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # End of record (\r\n)
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                i += 2  # skip \r\n
            elif text[i] == '\n':
                # End of record (\n)
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                i += 1  # skip \n
            else:
                raise ValueError(f"Invalid character after field at position {i}")
        else:
            # End of input
            current_record.append(current_field)
            records.append(current_record)
    
    return records
