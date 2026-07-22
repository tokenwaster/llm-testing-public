def parse_csv(text: str) -> list[list[str]]:
    """RFC-4180-style CSV parser (no csv module).

    - Comma-separated fields, records ended by \n or \r\n.
    - Fields starting with a double quote may contain commas, newlines,
      and doubled quotes ("" -> ").
    - Quotes are only special at the start of a field.
    - Raises ValueError on an unterminated quote or on stray characters
      after a closing quote.
    """
    records: list[list[str]] = []
    n = len(text)
    i = 0

    while i < n:
        fields: list[str] = []
        while True:
            # --- parse one field starting at i ---
            if i < n and text[i] == '"':
                # quoted field
                i += 1
                buf: list[str] = []
                closed = False
                while i < n:
                    c = text[i]
                    if c == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            buf.append('"')
                            i += 2
                        else:
                            i += 1
                            closed = True
                            break
                    else:
                        buf.append(c)
                        i += 1
                if not closed:
                    raise ValueError("unterminated quoted field")
                fields.append("".join(buf))
                # after a closing quote only comma, newline, or EOF is legal
                if i < n and text[i] not in (",", "\n", "\r"):
                    raise ValueError(
                        f"unexpected character {text[i]!r} after closing quote"
                    )
            else:
                # unquoted field: runs to comma, \n, \r\n, or EOF;
                # a lone \r is just a literal character
                start = i
                while i < n:
                    c = text[i]
                    if c == "," or c == "\n":
                        break
                    if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                        break
                    i += 1
                fields.append(text[start:i])

            # --- separator after the field ---
            if i >= n:
                records.append(fields)
                return records
            c = text[i]
            if c == ",":
                i += 1
                continue  # next field of the same record
            if c == "\n":
                i += 1
                break  # record complete
            if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                break  # record complete
            # only reachable via a bare \r right after a closing quote
            raise ValueError("unexpected character after closing quote")

        records.append(fields)

    return records
