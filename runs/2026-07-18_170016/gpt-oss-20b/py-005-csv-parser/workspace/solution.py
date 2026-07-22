#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data into a list of rows, each row being a list of fields.

    Parameters
    ----------
    text : str
        The CSV input string.

    Returns
    -------
    list[list[str]]
        Parsed records.

    Raises
    ------
    ValueError
        If the input is malformed (unclosed quotes or invalid characters after closing quote).
    """
    if text == "":
        return []

    rows: list[list[str]] = []
    field_chars: list[str] = []
    row: list[str] = []

    i = 0
    n = len(text)

    def add_field():
        nonlocal field_chars, row
        row.append("".join(field_chars))
        field_chars = []

    while i < n:
        ch = text[i]

        # Handle quoted field start
        if ch == '"':
            i += 1
            # Consume characters until closing quote
            while i < n:
                c = text[i]
                if c == '"':
                    # Check for escaped double quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote found
                        i += 1
                        break
                else:
                    field_chars.append(c)
                    i += 1
            else:
                # EOF reached without closing quote
                raise ValueError("Unclosed quoted field")

            # After closing quote, next char must be comma, newline or EOF
            if i < n and text[i] not in {',', '\n'}:
                # Allow \r\n: if we see \r, the next should be \n
                if text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                    pass
                else:
                    raise ValueError(f"Invalid character after closing quote at position {i}: '{text[i]}'")

            # If we hit a comma, consume it and continue to next field
            if i < n and text[i] == ',':
                add_field()
                i += 1
                continue

        elif ch == ',':
            # Empty field before comma
            add_field()
            i += 1
            continue

        elif ch in {'\n', '\r'}:
            # End of record
            if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            add_field()
            rows.append(row)
            row = []
            continue

        else:
            # Unquoted field character
            field_chars.append(ch)
            i += 1
            continue

    # End of input: if we are in the middle of a record, finalize it
    if field_chars or row:
        add_field()
        rows.append(row)

    return rows
