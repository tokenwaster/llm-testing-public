#!/usr/bin/env python3
"""
RFC‑4180 CSV parser implemented from scratch.
"""

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing RFC‑4180 style CSV data and return a list of rows,
    each row being a list of fields.

    Raises ValueError for malformed input.
    """
    if text == "":
        return []

    rows = []
    i = 0
    n = len(text)

    def peek(offset=0):
        return text[i + offset] if i + offset < n else None

    while i < n:
        # Start a new record
        row = []
        field = ""
        in_quotes = False
        quoted_field_started = False

        while True:
            ch = peek()
            if ch is None:  # EOF
                break
            if not in_quotes and ch == ',':
                # End of field
                row.append(field)
                field = ""
                i += 1
                continue
            if not in_quotes and (ch == '\n' or ch == '\r'):
                # End of record
                break
            if not quoted_field_started and ch == '"':
                # Start of a quoted field
                in_quotes = True
                quoted_field_started = True
                i += 1
                continue
            if in_quotes:
                if ch == '"':
                    # Possible end or escaped quote
                    nxt = peek(1)
                    if nxt == '"':  # Escaped quote
                        field += '"'
                        i += 2
                        continue
                    else:          # End of quoted field
                        in_quotes = False
                        i += 1
                        # After closing quote, next must be comma or line break or EOF
                        nxt2 = peek()
                        if nxt2 is None:
                            break
                        if nxt2 == ',':
                            row.append(field)
                            field = ""
                            i += 1
                            continue
                        if nxt2 in ('\n', '\r'):
                            break
                        # Any other character after closing quote is error
                        raise ValueError(f"Invalid character '{nxt2}' after closing quote at position {i}")
                else:
                    field += ch
                    i += 1
                    continue
            else:
                # Unquoted field content
                if ch in ('"', '\r', '\n'):
                    # These should have been handled above; treat as error
                    raise ValueError(f"Unexpected character '{ch}' at position {i}")
                field += ch
                i += 1

        # End of record reached
        row.append(field)
        rows.append(row)

        # Consume line break if present
        if peek() == '\r':
            i += 1
            if peek() == '\n':
                i += 1
        elif peek() == '\n':
            i += 1

    return rows
