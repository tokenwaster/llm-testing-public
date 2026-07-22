def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at position i ---
        if i < n and text[i] == '"':
            # quoted field: quotes are special only when the field starts with one
            i += 1
            buf: list[str] = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        buf.append('"')
                        i += 2
                    else:
                        i += 1  # consume closing quote
                        break
                else:
                    buf.append(c)
                    i += 1
            field = "".join(buf)
        else:
            # unquoted field: read until comma / newline / EOF
            start = i
            while i < n and text[i] not in (",", "\n", "\r"):
                i += 1
            field = text[start:i]

        row.append(field)

        # --- determine what follows the field ---
        if i >= n:
            records.append(row)
            break

        c = text[i]
        if c == ",":
            i += 1
            continue
        elif c in ("\r", "\n"):
            if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
            records.append(row)
            row = []
            if i >= n:
                # trailing newline does not create an extra record
                break
            continue
        else:
            # characters after a closing quote that aren't comma/newline/EOF
            raise ValueError(f"invalid character {c!r} after quoted field")

    return records
