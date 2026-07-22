def parse_csv(text: str) -> list[list[str]]:
    records = []
    field_chars = []
    row = []
    in_quotes = False
    just_closed = False
    field_is_quoted = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')
                    i += 2
                else:
                    in_quotes = False
                    just_closed = True
                    i += 1
            else:
                field_chars.append(c)
                i += 1
        else:
            if just_closed:
                if c == ',':
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    just_closed = False
                    i += 1
                elif c == '\n':
                    had_content = bool(field_chars) or bool(row) or field_is_quoted
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    if had_content:
                        records.append(row)
                    row = []
                    just_closed = False
                    i += 1
                elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                    had_content = bool(field_chars) or bool(row) or field_is_quoted
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    if had_content:
                        records.append(row)
                    row = []
                    just_closed = False
                    i += 2
                else:
                    raise ValueError("Unexpected character after closing quote")
            else:
                if c == '"' and not field_chars:
                    in_quotes = True
                    field_is_quoted = True
                    i += 1
                elif c == ',':
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    i += 1
                elif c == '\n':
                    had_content = bool(field_chars) or bool(row) or field_is_quoted
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    if had_content:
                        records.append(row)
                    row = []
                    i += 1
                elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                    had_content = bool(field_chars) or bool(row) or field_is_quoted
                    row.append(''.join(field_chars))
                    field_chars = []
                    field_is_quoted = False
                    if had_content:
                        records.append(row)
                    row = []
                    i += 2
                else:
                    field_chars.append(c)
                    i += 1

    if in_quotes:
        raise ValueError("Unclosed quote")

    if just_closed:
        row.append(''.join(field_chars))
        records.append(row)
    elif field_chars or row:
        row.append(''.join(field_chars))
        records.append(row)

    return records
