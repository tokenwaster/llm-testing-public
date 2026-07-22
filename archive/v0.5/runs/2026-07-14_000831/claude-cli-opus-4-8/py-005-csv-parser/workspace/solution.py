def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        # Parse one field starting at position i.
        if text[i] == '"':
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
            field = "".join(buf)
            # After a closing quote, only comma/newline/EOF are allowed.
            if i < n and text[i] not in (",", "\n", "\r"):
                raise ValueError("unexpected characters after closing quote")
        else:
            # Unquoted field: read until comma, newline, or EOF.
            start = i
            while i < n and text[i] not in (",", "\n", "\r"):
                i += 1
            field = text[start:i]

        fields.append(field)

        # Now decide what follows the field.
        if i >= n:
            # EOF ends the last record.
            records.append(fields)
            fields = []
            break
        c = text[i]
        if c == ",":
            i += 1
            # A comma means another field follows (possibly empty).
            continue
        elif c == "\n":
            i += 1
            records.append(fields)
            fields = []
        elif c == "\r":
            i += 1
            if i < n and text[i] == "\n":
                i += 1
            records.append(fields)
            fields = []

    # If input ended right after a record terminator, no trailing empty record.
    if fields:
        records.append(fields)

    return records
