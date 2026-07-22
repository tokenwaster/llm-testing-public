# solution.py

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a CSV string according to a subset of RFC‑4180.

    Parameters
    ----------
    text: str
        The CSV data.

    Returns
    -------
    list[list[str]]
        Parsed rows, each row being a list of field strings.

    Raises
    ------
    ValueError
        If the input is malformed (unclosed quote or stray characters after a
        closing quote).
    """
    rows: list[list[str]] = []
    current_row: list[str] = []
    current_field: list[str] = []

    # States:
    #   'start'        – at the beginning of a field
    #   'unquoted'     – reading an unquoted field
    #   'quoted'       – inside a quoted field
    #   'after_quote'  – just after a closing quote, expecting , or newline or EOF
    state = 'start'
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        # Helper to consume a CRLF as a single newline
        def consume_newline(idx: int) -> int:
            if text[idx] == '\r' and idx + 1 < n and text[idx + 1] == '\n':
                return idx + 2
            return idx + 1

        if state == 'start':
            if c == '"':
                state = 'quoted'
                i += 1
            elif c == ',':
                # empty field
                current_row.append('')
                i += 1
            elif c == '\r' or c == '\n':
                # empty field before newline
                current_row.append('')
                rows.append(current_row)
                current_row = []
                i = consume_newline(i)
            else:
                state = 'unquoted'
                current_field.append(c)
                i += 1

        elif state == 'unquoted':
            if c == ',':
                current_row.append(''.join(current_field))
                current_field = []
                state = 'start'
                i += 1
            elif c == '\r' or c == '\n':
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                state = 'start'
                i = consume_newline(i)
            else:
                current_field.append(c)
                i += 1

        elif state == 'quoted':
            if c == '"':
                # Look ahead: doubled quote -> literal quote, otherwise end of quoted field
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    state = 'after_quote'
                    i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == 'after_quote':
            if c == ',':
                current_row.append(''.join(current_field))
                current_field = []
                state = 'start'
                i += 1
            elif c == '\r' or c == '\n':
                current_row.append(''.join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                state = 'start'
                i = consume_newline(i)
            else:
                raise ValueError("Invalid character after closing quote")
        else:
            # Should never happen
            raise RuntimeError("Invalid parser state")

    # End of input – finalize any pending data
    if state == 'quoted':
        raise ValueError("Unclosed quoted field")
    elif state == 'after_quote' or state == 'unquoted':
        # Add the last field and the row it belongs to
        current_row.append(''.join(current_field))
        rows.append(current_row)
    elif state == 'start':
        # Possible pending empty field after a trailing comma
        if text and text[-1] == ',':
            current_row.append('')
        if current_row:
            rows.append(current_row)

    # Special case: empty input should yield an empty list
    if not rows:
        return []

    return rows
