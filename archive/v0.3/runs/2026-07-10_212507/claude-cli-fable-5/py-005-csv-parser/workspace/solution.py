def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of records (lists of fields)."""
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at i ---
        if i < n and text[i] == '"':
            # Quoted field
            i += 1
            buf: list[str] = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        buf.append('"')  # escaped quote
                        i += 2
                    else:
                        i += 1  # closing quote
                        break
                else:
                    buf.append(c)
                    i += 1
            field = "".join(buf)
            # After the closing quote only a comma, a record separator,
            # or EOF is allowed — anything else is malformed.
            if i < n:
                c = text[i]
                valid = (
                    c == ","
                    or c == "\n"
                    or (c == "\r" and i + 1 < n and text[i + 1] == "\n")
                )
                if not valid:
                    raise ValueError(
                        f"unexpected character {text[i]!r} after closing quote "
                        f"at position {i}"
                    )
        else:
            # Unquoted field: runs until comma, \n, or \r\n.
            # A quote inside (not at the start) is literal; a bare \r not
            # followed by \n is also literal content.
            start = i
            while i < n:
                c = text[i]
                if c == "," or c == "\n":
                    break
                if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                i += 1
            field = text[start:i]

        # --- handle what terminates the field ---
        if i >= n:
            fields.append(field)
            records.append(fields)
            break

        c = text[i]
        if c == ",":
            fields.append(field)
            i += 1
            continue

        # Record separator: \n or \r\n (guaranteed by the checks above).
        sep = 2 if c == "\r" else 1
        fields.append(field)
        records.append(fields)
        fields = []
        i += sep
        if i >= n:
            # Trailing newline: no extra empty record.
            break

    return records
