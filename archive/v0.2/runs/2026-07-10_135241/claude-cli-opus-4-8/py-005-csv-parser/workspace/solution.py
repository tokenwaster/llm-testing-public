def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of records (lists of fields)."""
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while True:
        # Parse one field starting at index i.
        if i < n and text[i] == '"':
            # Quoted field.
            i += 1
            buf = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        buf.append('"')
                        i += 2
                    else:
                        # Closing quote.
                        i += 1
                        closed = True
                        break
                else:
                    buf.append(c)
                    i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            # After closing quote, only comma/newline/EOF are allowed.
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError("unexpected characters after closing quote")
            field = "".join(buf)
        else:
            # Unquoted field: read until comma, newline, or EOF.
            start = i
            while i < n and text[i] not in (',', '\n', '\r'):
                i += 1
            field = text[start:i]

        fields.append(field)

        # Now at a delimiter, newline, or EOF.
        if i >= n:
            records.append(fields)
            break

        c = text[i]
        if c == ',':
            i += 1
            continue
        elif c == '\n' or c == '\r':
            # Consume the record separator (\n or \r\n).
            if c == '\r' and i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            records.append(fields)
            fields = []
            if i >= n:
                # Trailing newline: no extra record.
                break

    return records
