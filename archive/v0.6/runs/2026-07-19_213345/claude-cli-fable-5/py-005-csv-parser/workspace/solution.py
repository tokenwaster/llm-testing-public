def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at i ---
        if i < n and text[i] == '"':
            # quoted field
            i += 1
            buf = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        buf.append('"')
                        i += 2
                    else:
                        i += 1  # closing quote
                        break
                else:
                    buf.append(c)
                    i += 1
            field = "".join(buf)
        else:
            # unquoted field: runs until comma, \n, or \r\n
            start = i
            while i < n:
                c = text[i]
                if c == "," or c == "\n":
                    break
                if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                i += 1
            field = text[start:i]

        # --- delimiter after the field ---
        if i >= n:
            fields.append(field)
            records.append(fields)
            break

        c = text[i]
        if c == ",":
            fields.append(field)
            i += 1
            continue
        if c == "\n" or (c == "\r" and i + 1 < n and text[i + 1] == "\n"):
            fields.append(field)
            records.append(fields)
            fields = []
            i += 2 if c == "\r" else 1
            if i >= n:
                break  # trailing newline: no extra record
            continue

        # only reachable after a quoted field: stray char after closing quote
        raise ValueError(f"unexpected character {c!r} after closing quote")

    return records
