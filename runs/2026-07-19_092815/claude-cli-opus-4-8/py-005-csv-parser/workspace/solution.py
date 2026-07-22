def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    fields = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at position i ---
        if i < n and text[i] == '"':
            # quoted field
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
                        i += 1
                        closed = True
                        break
                else:
                    buf.append(c)
                    i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            field = "".join(buf)
        else:
            # unquoted field: quotes are literal here
            buf = []
            while i < n and text[i] not in (",", "\n", "\r"):
                buf.append(text[i])
                i += 1
            field = "".join(buf)

        fields.append(field)

        # --- now at a separator or EOF ---
        if i >= n:
            records.append(fields)
            break

        c = text[i]
        if c == ",":
            i += 1
            continue
        elif c == "\n":
            i += 1
            records.append(fields)
            fields = []
            if i >= n:
                break
            continue
        elif c == "\r":
            if i + 1 < n and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
            records.append(fields)
            fields = []
            if i >= n:
                break
            continue
        else:
            # character after a closing quote that isn't comma/newline/EOF
            raise ValueError("invalid character after quoted field")

    return records
