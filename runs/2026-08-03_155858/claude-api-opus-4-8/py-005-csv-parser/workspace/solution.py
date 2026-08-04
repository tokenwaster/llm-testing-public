def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    field = []
    record = []
    i = 0
    n = len(text)

    field_start = True  # are we at the start of a field?
    in_quotes = False
    after_close = False  # just closed a quoted field, awaiting , or newline or EOF

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    after_close = True
                    i += 1
                    continue
            else:
                field.append(c)
                i += 1
                continue

        if after_close:
            if c == ',':
                record.append(''.join(field))
                field = []
                field_start = True
                after_close = False
                i += 1
                continue
            elif c == '\n':
                record.append(''.join(field))
                field = []
                records.append(record)
                record = []
                field_start = True
                after_close = False
                i += 1
                continue
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    record.append(''.join(field))
                    field = []
                    records.append(record)
                    record = []
                    field_start = True
                    after_close = False
                    i += 2
                    continue
                else:
                    raise ValueError("invalid character after closing quote")
            else:
                raise ValueError("invalid character after closing quote")

        # not in quotes, not after close
        if field_start and c == '"':
            in_quotes = True
            field_start = False
            i += 1
            continue

        field_start = False

        if c == ',':
            record.append(''.join(field))
            field = []
            field_start = True
            i += 1
            continue
        elif c == '\n':
            record.append(''.join(field))
            field = []
            records.append(record)
            record = []
            field_start = True
            i += 1
            continue
        elif c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                record.append(''.join(field))
                field = []
                records.append(record)
                record = []
                field_start = True
                i += 2
                continue
            else:
                record.append(''.join(field))
                field = []
                records.append(record)
                record = []
                field_start = True
                i += 1
                continue
        else:
            field.append(c)
            i += 1
            continue

    if in_quotes:
        raise ValueError("unterminated quoted field")

    # end of input: flush remaining field/record
    record.append(''.join(field))
    records.append(record)

    return records
