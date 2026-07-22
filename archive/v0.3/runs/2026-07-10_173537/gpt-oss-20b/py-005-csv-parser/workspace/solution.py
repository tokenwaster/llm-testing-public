#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data and return a list of rows,
    each row being a list of fields.

    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    rows = []
    field = ""
    in_quotes = False
    i = 0
    length = len(text)

    def add_field():
        nonlocal field, rows
        rows[-1].append(field)
        field = ""

    while i < length:
        ch = text[i]

        if in_quotes:
            if ch == '"':
                # Peek next character to see if it's an escaped quote
                if i + 1 < length and text[i + 1] == '"':
                    field += '"'
                    i += 1  # skip the second quote
                else:
                    # End of quoted field
                    in_quotes = False
            else:
                field += ch

        else:  # not inside quotes
            if ch == ',':
                add_field()
            elif ch == '\n':
                add_field()
                rows.append([])
            elif ch == '\r':
                # Handle CRLF
                if i + 1 < length and text[i + 1] == '\n':
                    i += 1  # skip the LF part of CRLF
                add_field()
                rows.append([])
            elif ch == '"':
                if field != "":
                    # Quote only special at start of field
                    raise ValueError(f"Unexpected quote at position {i}")
                in_quotes = True
            else:
                field += ch

        i += 1

    # End of input: finalize last field/row
    if in_quotes:
        raise ValueError("Unclosed quoted field at end of input")

    add_field()
    rows.append([])

    # Remove trailing empty row caused by final newline (if any)
    if rows and all(f == "" for f in rows[-1]) and len(rows) > 1:
        rows.pop()

    return rows
