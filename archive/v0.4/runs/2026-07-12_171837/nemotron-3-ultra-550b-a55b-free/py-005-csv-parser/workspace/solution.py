def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    state = 'START_FIELD'  # 'START_FIELD', 'IN_UNQUOTED', 'IN_QUOTED', 'AFTER_QUOTE'

    while i < n:
        ch = text[i]
        if state == 'START_FIELD':
            if ch == '"':
                state = 'IN_QUOTED'
                i += 1
            elif ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif ch == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    current_field.append(ch)
                    state = 'IN_UNQUOTED'
                    i += 1
            else:
                current_field.append(ch)
                state = 'IN_UNQUOTED'
                i += 1

        elif state == 'IN_UNQUOTED':
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'START_FIELD'
                    i += 2
                else:
                    current_field.append(ch)
                    i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 'IN_QUOTED':
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    state = 'AFTER_QUOTE'
                    i += 1
            elif ch == '\r' or ch == '\n':
                current_field.append(ch)
                i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 'AFTER_QUOTE':
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'START_FIELD'
                    i += 2
                else:
                    raise ValueError("Invalid character after closing quote")
            else:
                raise ValueError("Invalid character after closing quote")

    # Finalization after processing all characters
    if state == 'IN_QUOTED':
        raise ValueError("Unclosed quoted field")
    elif state == 'AFTER_QUOTE':
        current_record.append(''.join(current_field))
        current_field = []
        records.append(current_record)
    elif state == 'IN_UNQUOTED':
        current_record.append(''.join(current_field))
        current_field = []
        records.append(current_record)
    elif state == 'START_FIELD':
        if current_record:
            current_record.append(''.join(current_field))
            records.append(current_record)

    return records
