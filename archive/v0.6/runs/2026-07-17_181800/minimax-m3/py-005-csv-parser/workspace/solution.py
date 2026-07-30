def parse_csv(text: str) -> list[list[str]]:
    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)
    # state: 'start' | 'unquoted' | 'quoted' | 'quote_in_quoted'
    state = 'start'

    while i < n:
        c = text[i]
        if state == 'start':
            if c == '"':
                state = 'quoted'
                i += 1
            elif c == ',':
                record.append(''.join(field))
                field = []
                i += 1
            elif c == '\n':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                i += 1
            elif c == '\r':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                field.append(c)
                state = 'unquoted'
                i += 1
        elif state == 'unquoted':
            if c == ',':
                record.append(''.join(field))
                field = []
                state = 'start'
                i += 1
            elif c == '\n':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'start'
                i += 1
            elif c == '\r':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'start'
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                field.append(c)
                i += 1
        elif state == 'quoted':
            if c == '"':
                state = 'quote_in_quoted'
                i += 1
            else:
                field.append(c)
                i += 1
        else:  # quote_in_quoted
            if c == '"':
                field.append('"')
                state = 'quoted'
                i += 1
            elif c == ',':
                record.append(''.join(field))
                field = []
                state = 'start'
                i += 1
            elif c == '\n':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'start'
                i += 1
            elif c == '\r':
                record.append(''.join(field))
                records.append(record)
                record = []
                field = []
                state = 'start'
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                raise ValueError(
                    f"Unexpected character {c!r} after closing quote at position {i}"
                )

    # End of input handling
    if state == 'start':
        # Trailing newline case: record is empty, do nothing.
        # Otherwise (e.g. trailing comma), finalize the pending field.
        if record:
            record.append(''.join(field))
            records.append(record)
    elif state == 'unquoted':
        record.append(''.join(field))
        records.append(record)
    elif state == 'quoted':
        raise ValueError("Unclosed quoted field")
    else:  # quote_in_quoted
        record.append(''.join(field))
        records.append(record)

    return records
