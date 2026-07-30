def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)

    def end_field():
        nonlocal field
        row.append("".join(field))
        field = []

    def end_row():
        nonlocal row
        end_field()
        rows.append(row)
        row = []

    while i < n:
        c = text[i]

        if c == '"':
            # Quoted field — only special if field starts with quote
            if field:
                # Quote in the middle of an unquoted field: literal
                field.append(c)
                i += 1
                continue

            # Start of quoted field
            i += 1
            while True:
                if i >= n:
                    raise ValueError("unclosed quote")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        # After closing quote: must be comma, newline, or EOF
                        if i < n:
                            nxt = text[i]
                            if nxt == ',':
                                end_field()
                                i += 1
                                break
                            elif nxt == '\n':
                                end_row()
                                i += 1
                                break
                            elif nxt == '\r':
                                if i + 1 < n and text[i + 1] == '\n':
                                    i += 1
                                end_row()
                                i += 1
                                break
                            else:
                                raise ValueError("characters after closing quote")
                        else:
                            # EOF after closing quote
                            end_field()
                            break
                else:
                    field.append(c)
                    i += 1
            continue

        if c == ',':
            end_field()
            i += 1
            continue

        if c == '\n':
            end_row()
            i += 1
            continue

        if c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                i += 1
            end_row()
            i += 1
            continue

        # Regular character
        field.append(c)
        i += 1

    # Handle end of input
    # If we ended right after a row terminator, row and field are empty — no extra record
    # Trailing newline does not create an extra record
    if field or row:
        # There's pending content (or empty fields like trailing comma)
        end_row()
    elif not rows:
        # Input was something that produced nothing? shouldn't happen for non-empty
        pass

    # Special case: input that is only newlines / empty lines
    # Actually for "\n" — we call end_row once when we see \n, leaving row/field empty
    # so we get one row [""]. Good.
    # For "a\n" — we end_row on \n with field=['a'], then row/field empty at EOF — no extra. Good.
    # For "" — return []. Good.

    return rows
