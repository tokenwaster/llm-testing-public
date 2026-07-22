def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        if not current_field:
            if char == '"':
                i += 1
                while i < n:
                    char = text[i]
                    if char == '"':
                        if i + 1 < n:
                            next_char = text[i+1]
                            if next_char == '"':
                                current_field.append('"')
                                i += 2
                            elif next_char == ',':
                                current_record.append(''.join(current_field))
                                current_field = []
                                i += 2
                                break
                            elif next_char == '\r':
                                if i + 2 < n and text[i+2] == '\n':
                                    current_record.append(''.join(current_field))
                                    current_field = []
                                    if current_record and (current_record != [''] or i + 2 < n):
                                        records.append(current_record)
                                        current_record = []
                                    i += 3
                                    break
                                else:
                                    raise ValueError("Malformed CSV")
                            elif next_char == '\n':
                                current_record.append(''.join(current_field))
                                current_field = []
                                if current_record and (current_record != [''] or i + 1 < n):
                                    records.append(current_record)
                                    current_record = []
                                i += 2
                                break
                            else:
                                raise ValueError("Malformed CSV")
                        else:
                            current_record.append(''.join(current_field))
                            current_field = []
                            if current_record and (current_record != [''] or i < n):
                                records.append(current_record)
                                current_record = []
                            break
                    elif char == '\r':
                        if i + 1 < n and text[i+1] == '\n':
                            current_field.append('\r\n')
                            i += 2
                        else:
                            current_field.append('\r')
                            i += 1
                    elif char == '\n':
                        current_field.append('\n')
                        i += 1
                    else:
                        current_field.append(char)
                        i += 1
                continue
            else:
                if char == ',':
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
                    continue
                elif char == '\r':
                    if i + 1 < n and text[i+1] == '\n':
                        current_record.append(''.join(current_field))
                        current_field = []
                        if current_record and (current_record != [''] or i + 2 < n):
                            records.append(current_record)
                            current_record = []
                        i += 2
                        continue
                    else:
                        current_field.append('\r')
                        i += 1
                        continue
                elif char == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    if current_record and (current_record != [''] or i + 1 < n):
                        records.append(current_record)
                        current_record = []
                    i += 1
                    continue
                else:
                    current_field.append(char)
                    i += 1
                    continue
        else:
            if char == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
                continue
            elif char == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    if current_record and (current_record != [''] or i + 2 < n):
                        records.append(current_record)
                        current_record = []
                    i += 2
                    continue
                else:
                    current_field.append('\r')
                    i += 1
                    continue
            elif char == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                if current_record and (current_record != [''] or i + 1 < n):
                    records.append(current_record)
                    current_record = []
                i += 1
                continue
            else:
                current_field.append(char)
                i += 1
                continue

    if current_field or current_record:
        current_record.append(''.join(current_field))
        records.append(current_record)
        
    return records
