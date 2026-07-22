def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at i ---
        if i < n and text[i] == '"':
            # Quoted field: consume until the closing quote, decoding "" -> "
            i += 1
            chars: list[str] = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1  # closing quote
                        break
                else:
                    chars.append(c)
                    i += 1
            field = "".join(chars)
        else:
            # Unquoted field: runs to the next comma, \n, or \r\n.
            # A lone \r (not followed by \n) is a literal character.
            chars = []
            while i < n:
                c = text[i]
                if c == "," or c == "\n":
                    break
                if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                chars.append(c)
                i += 1
            field = "".join(chars)

        row.append(field)

        # --- what follows the field must be , newline, or EOF ---
        if i >= n:
            rows.append(row)
            break

        c = text[i]
        if c == ",":
            i += 1
            continue  # next field in the same record

        if c == "\n":
            i += 1
        elif c == "\r" and i + 1 < n and text[i + 1] == "\n":
            i += 2
        else:
            # Only reachable after a quoted field, e.g. "ab"x
            raise ValueError(f"unexpected character {c!r} after closing quote")

        rows.append(row)
        row = []
        if i >= n:
            break  # trailing newline: no extra record

    return rows
