def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []
    
    records = []
    current_record = []
    i = 0
    n = len(text)
    last_char_was_newline = False

    while i < n:
        current_field = []
        if text[i] == '"':  # Quoted field
            i += 1
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i+1] == '"':
                        current_field.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        break
                else:
                    current_field.append(text[i])
                    i += 1
            
            if i < n and text[i] == ',':
                current_record.append("".join(current_field))
                i += 1
                last_char_was_newline = False
                continue
            elif i < n and text[i] in ('\n', '\r'):
                if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                last_char_was_newline = True
                continue
            elif i == n:
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                last_char_was_newline = False
                break
            else:
                raise ValueError("Malformed input")
        else:  # Unquoted field
            while i < n and text[i] not in (',', '\n', '\r'):
                current_field.append(text[i])
                i += 1
            
            if i < n and text[i] == ',':
                current_record.append("".join(current_field))
                i += 1
                last_char_was_newline = False
                continue
            elif i < n and text[i] in ('\n', '\r'):
                if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                last_char_was_newline = True
                continue
            elif i == n:
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                last_char_was_newline = False
                break

    # Handle cases where the string ends with a comma (e.g., "a,")
    if i == n and not last_char_was_newline and i > 0 and text[i-1] == ',':
        current_record.append("")
        records.append(current_record)

    return records
