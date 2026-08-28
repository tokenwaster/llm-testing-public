def parse_csv(text: str) -> list[list[str]]:
    rows = []
    row = []
    field_chars = []
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if not in_quotes:
            if c == ',':
                row.append(''.join(field_chars))
                field_chars = []
                i += 1
                continue
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    row.append(''.join(field_chars))
                    field_chars = []
                    rows.append(row)
                    row = []
                    i += 2
                    continue
                else:
                    row.append(''.join(field_chars))
                    field_chars = []
                    rows.append(row)
                    row = []
                    i += 1
                    continue
            elif c == '\n':
                row.append(''.join(field_chars))
                field_chars = []
                rows.append(row)
                row = []
                i += 1
                continue
            elif c == '"':
                if field_chars == []:
                    in_quotes = True
                    i += 1
                    continue
                else:
                    field_chars.append(c)
                    i += 1
                    continue
            else:
                field_chars.append(c)
                i += 1
                continue
        else:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    i += 1
                    if i < n:
                        nxt = text[i]
                        if nxt != ',' and nxt != '\r' and nxt != '\n':
                            raise ValueError('Invalid character after closing quote')
                    continue
            else:
                field_chars.append(c)
                i += 1
                continue

    if in_quotes:
        raise ValueError('Unclosed quote')

    if field_chars or row:
        row.append(''.join(field_chars))
        if row:
            rows.append(row)

    return rows
