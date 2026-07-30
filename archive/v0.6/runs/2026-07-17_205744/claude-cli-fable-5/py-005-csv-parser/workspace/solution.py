def parse_csv(text: str) -> list[list[str]]:
    """RFC-4180-style CSV parser, written from scratch (no csv module)."""
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        # --- parse one field ---
        if text[i] == '"':
            # Quoted field: consume until the closing quote, decoding "" -> "
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
                        i += 1  # closing quote
                        break
                else:
                    buf.append(c)
                    i += 1
            field = "".join(buf)
        else:
            # Unquoted field: runs until comma, \n, \r\n, or EOF.
            # Quotes inside it are literal (field doesn't start with a quote).
            j = i
            while j < n:
                c = text[j]
                if c == ',' or c == '\n':
                    break
                if c == '\r' and j + 1 < n and text[j + 1] == '\n':
                    break
                j += 1
            field = text[i:j]
            i = j

        fields.append(field)

        # --- what follows the field must be a comma, newline, or EOF ---
        if i >= n:
            break
        c = text[i]
        if c == ',':
            i += 1
            if i >= n:
                # trailing comma: one final empty field
                fields.append("")
                break
        elif c == '\n':
            i += 1
            records.append(fields)
            fields = []
        elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
            i += 2
            records.append(fields)
            fields = []
        else:
            # only reachable after a closed quoted field, e.g. "ab"x
            raise ValueError(f"unexpected character {c!r} after closing quote")

    if fields:
        records.append(fields)
    return records
