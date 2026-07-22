def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    i = 0
    
    while i < len(text):
        record = []
        
        while True:
            field, new_i = _parse_field(text, i)
            record.append(field)
            i = new_i
            
            if i >= len(text):
                break
            
            c = text[i]
            if c == ',':
                i += 1
            elif c == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                i += 2
                break
            elif c == '\n':
                i += 1
                break
            else:
                raise ValueError(f"Unexpected character after field: {c!r}")
        
        records.append(record)
    
    return records


def _parse_field(text, start):
    if text[start] == '"':
        # Quoted field
        i = start + 1
        chars = []
        
        while i < len(text):
            c = text[i]
            if c == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    # Escaped quote
                    chars.append('"')
                    i += 2
                else:
                    # Closing quote
                    i += 1
                    if i >= len(text):
                        return ''.join(chars), i
                    c = text[i]
                    if c == ',':
                        return ''.join(chars), i + 1
                    elif c == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                        return ''.join(chars), i + 2
                    elif c == '\n':
                        return ''.join(chars), i + 1
                    else:
                        raise ValueError(f"Invalid character after closing quote: {c!r}")
            else:
                chars.append(c)
                i += 1
        
        raise ValueError("Unclosed quoted field")
    else:
        # Unquoted field - read until comma or newline
        i = start
        chars = []
        
        while i < len(text):
            c = text[i]
            if c == ',' or c == '\n':
                break
            if c == '\r' and (i + 1 >= len(text) or text[i + 1] != '\n'):
                # Bare \r, include in field content
                chars.append(c)
                i += 1
            elif c == '\r' and i + 1 < len(text) and text[i + 1] == '\n':
                # \r\n is a record separator
                break
            else:
                chars.append(c)
                i += 1
        
        return ''.join(chars), i
