def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    state = 'FIELD_START'  # FIELD_START | UNQUOTED | QUOTED | AFTER_QUOTE
    record_committed = False
    i = 0
    n = len(text)

    def commit_record() -> None:
        nonlocal record, field, record_committed
        record.append(''.join(field))
        field = []
        records.append(record)
        record = []
        record_committed = True

    while i < n:
        c = text[i]
        record_committed = False

        if state == 'FIELD_START':
            if c == '"':
                state = 'QUOTED'
                i += 1
            elif c == ',':
                record.append('')
                i += 1
            elif c == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 2
            else:
                field.append(c)
                state = 'UNQUOTED'
                i += 1

        elif state == 'UNQUOTED':
            if c == ',':
                record.append(''.join(field))
                field = []
                state = 'FIELD_START'
                i += 1
            elif c == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 2
            else:
                field.append(c)
                i += 1

        elif state == 'QUOTED':
            if c == '"':
                state = 'AFTER_QUOTE'
                i += 1
            else:
                field.append(c)
                i += 1

        else:  # AFTER_QUOTE
            if c == '"':
                field.append('"')
                state = 'QUOTED'
                i += 1
            elif c == ',':
                record.append(''.join(field))
                field = []
                state = 'FIELD_START'
                i += 1
            elif c == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                commit_record()
                state = 'FIELD_START'
                i += 2
            else:
                raise ValueError(
                    "Unexpected character after closing quote: " + repr(c)
                )

    if record_committed:
        pass
    elif state == 'FIELD_START':
        record.append('')
        records.append(record)
    elif state == 'UNQUOTED':
        record.append(''.join(field))
        records.append(record)
    elif state == 'QUOTED':
        raise ValueError("Unclosed quoted field")
    else:  # AFTER_QUOTE
        record.append(''.join(field))
        records.append(record)

    return records
