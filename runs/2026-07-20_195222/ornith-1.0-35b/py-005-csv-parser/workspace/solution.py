def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    i = 0
    n = len(text)
    
    while i < n:
        record = []
        
        while True:
            if i >= n:
                break
            
            if text[i] == '"':
                # Quoted field — parse until closing quote (handling "" escapes)
                i += 1  # skip opening quote
                field_chars = []
                found_closing_quote = False
                
                while i < n:
                    if text[i] == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            # Escaped double-quote: "" → "
                            field_chars.append('"')
                            i += 2
                        else:
                            # Closing quote
                            found_closing_quote = True
                            i += 1
                            break
                    else:
                        field_chars.append(text[i])
                        i += 1
                
                if not found_closing_quote:
                    raise ValueError("Unclosed quoted field")
                
                record.append(''.join(field_chars))
                
                # After closing quote, only comma / newline / EOF are valid
                if i >= n:
                    break  # EOF → end of record
                elif text[i] == ',':
                    i += 1
                    if i >= n:
                        # Trailing comma means an empty field follows
                        record.append("")
                        break
                    continue  # next field in same record
                elif text[i] == '\n':
                    i += 1
                    break  # end of record
                elif text[i] == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2  # consume \r\n together
                    else:
                        raise ValueError("Invalid character after closing quote")
                    break  # end of record
                else:
                    raise ValueError(f"Invalid character after closing quote: {text[i]!r}")
            else:
                # Unquoted field — read until comma or newline
                field_chars = []
                while i < n and text[i] not in (',', '\n'):
                    field_chars.append(text[i])
                    i += 1
                
                record.append(''.join(field_chars))
                
                if i >= n:
                    break  # EOF → end of record
                
                if text[i] == ',':
                    i += 1
                    if i >= n:
                        # Trailing comma means an empty field follows
                        record.append("")
                        break
                    continue  # next field in same record
                elif text[i] == '\n':
                    i += 1
                    break  # end of record
                else:
                    raise ValueError(f"Unexpected character: {text[i]!r}")
        
        records.append(record)
    
    return records
