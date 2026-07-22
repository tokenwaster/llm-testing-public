def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    while i <= n:
        # Parse one field starting at position i.
        if i < n and text[i] == '"':
            # Quoted field.
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
            fields.append("".join(chars))
            # After closing quote: must be comma, newline, or EOF.
            if i >= n:
                records.append(fields)
                return records
            c = text[i]
            if c == ',':
                i += 1
                if i == n:  # trailing comma -> final empty field
                    fields.append("")
                    records.append(fields)
                    return records
                continue
            elif c == '\n':
                records.append(fields)
                fields = []
                i += 1
                if i == n:
                    return records
                continue
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                records.append(fields)
                fields = []
                i += 2
                if i == n:
                    return records
                continue
            else:
                raise ValueError("unexpected character after closing quote")
        else:
            # Unquoted field: read until comma, newline, or EOF.
            start = i
            while i < n and text[i] != ',' and text[i] != '\n' and not (
                text[i] == '\r' and i + 1 < n and text[i + 1] == '\n'
            ):
                i += 1
            fields.append(text[start:i])
            if i >= n:
                records.append(fields)
                return records
            c = text[i]
            if c == ',':
                i += 1
                if i == n:
                    fields.append("")
                    records.append(fields)
                    return records
            elif c == '\n':
                records.append(fields)
                fields = []
                i += 1
                if i == n:
                    return records
            else:  # '\r\n'
                records.append(fields)
                fields = []
                i += 2
                if i == n:
                    return records

    return records
