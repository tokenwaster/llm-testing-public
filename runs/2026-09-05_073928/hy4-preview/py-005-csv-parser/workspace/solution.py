def parse_csv(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    record: list[str] = []
    field_chars: list[str] = []
    in_quotes = False
    at_field_start = True
    record_started = False
    field_open = False

    i = 0
    n = len(text)

    while i < n:
        if not record_started:
            # Begin a new record and its first (possibly empty) field.
            record_started = True
            record = []
            field_chars = []
            field_open = True
            in_quotes = False
            at_field_start = True

        c = text[i]

        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped double-quote inside a quoted field.
                    field_chars.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote.
                    in_quotes = False
                    i += 1
                    # Only a delimiter or EOF may follow a closing quote.
                    if i < n:
                        nc = text[i]
                        if nc == ',' or nc == '\n':
                            pass
                        elif nc == '\r' and i + 1 < n and text[i + 1] == '\n':
                            pass
                        else:
                            raise ValueError("unexpected character after closing quote")
                    continue
            else:
                # Commas and newlines are literal inside quotes.
                field_chars.append(c)
                i += 1
                continue

        # Not inside quotes.
        if c == '"' and at_field_start:
            # Opening quote: field is quoted.
            in_quotes = True
            at_field_start = False
            i += 1
            continue

        if c == ',':
            # End of field.
            record.append(''.join(field_chars))
            field_chars = []
            field_open = True
            at_field_start = True
            in_quotes = False
            i += 1
            continue

        if c == '\n':
            # End of record (LF).
            record.append(''.join(field_chars))
            rows.append(record)
            record_started = False
            record = []
            field_chars = []
            field_open = False
            at_field_start = True
            in_quotes = False
            i += 1
            continue

        if c == '\r' and i + 1 < n and text[i + 1] == '\n':
            # End of record (CRLF).
            record.append(''.join(field_chars))
            rows.append(record)
            record_started = False
            record = []
            field_chars = []
            field_open = False
            at_field_start = True
            in_quotes = False
            i += 2
            continue

        # Ordinary character (including a lone \r, or a quote not at field start).
        field_chars.append(c)
        at_field_start = False
        i += 1

    # End of input.
    if in_quotes:
        raise ValueError("unclosed quoted field")

    if record_started:
        # Finalize the last field and record.
        if field_open:
            record.append(''.join(field_chars))
        rows.append(record)

    return rows
