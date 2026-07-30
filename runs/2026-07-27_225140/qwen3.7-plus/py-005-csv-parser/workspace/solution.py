def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)

    state = 'field_start'  # 'field_start', 'unquoted', 'quoted', 'after_quote'

    while i < n:
        c = text[i]

        if state == 'field_start':
            if c == '"':
                state = 'quoted'
                i += 1
            elif c == ',':
                current_record.append('')
                i += 1
            elif c == '\n':
                current_record.append('')
                records.append(current_record)
                current_record = []
                i += 1
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append('')
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    current_field.append(c)
                    state = 'unquoted'
                    i += 1
            else:
                current_field.append(c)
                state = 'unquoted'
                i += 1

        elif state == 'unquoted':
            if c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'field_start'
                i += 1
            elif c == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'field_start'
                i += 1
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'field_start'
                    i += 2
                else:
                    current_field.append(c)
                    i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == 'quoted':
            if c == '"':
                state = 'after_quote'
                i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == 'after_quote':
            if c == '"':
                current_field.append('"')
                state = 'quoted'
                i += 1
            elif c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'field_start'
                i += 1
            elif c == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'field_start'
                i += 1
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'field_start'
                    i += 2
                else:
                    raise ValueError(
                        f"Invalid character after closing quote: {c!r}"
                    )
            else:
                raise ValueError(
                    f"Invalid character after closing quote: {c!r}"
                )

    # Handle end of input
    if state == 'quoted':
        raise ValueError("Unclosed quote")

    if state == 'field_start':
        if current_record:
            # Input ended with a comma — finalize with an empty trailing field
            current_record.append('')
            records.append(current_record)
        # else: trailing newline — do not create an extra empty record
    elif state in ('unquoted', 'after_quote'):
        current_record.append(''.join(current_field))
        records.append(current_record)

    return records
