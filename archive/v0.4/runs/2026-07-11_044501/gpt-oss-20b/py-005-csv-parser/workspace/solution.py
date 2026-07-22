#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing RFC‑4180 CSV data and return a list of rows,
    each row being a list of fields.

    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    rows = []
    i = 0
    n = len(text)

    while i < n:
        # Parse one record
        row = []
        field = ""
        in_quotes = False

        while True:
            if i >= n:  # end of file
                break

            ch = text[i]

            if not in_quotes:
                if ch == ',':
                    # End of field
                    row.append(field)
                    field = ""
                    i += 1
                elif ch == '\r':
                    # Handle CRLF or lone CR
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    row.append(field)
                    field = ""
                    break  # end of record
                elif ch == '\n':
                    i += 1
                    row.append(field)
                    field = ""
                    break  # end of record
                elif ch == '"':
                    in_quotes = True
                    i += 1
                else:
                    field += ch
                    i += 1
            else:  # inside quoted field
                if ch == '"':
                    # Possible escaped quote or closing quote
                    if i + 1 < n and text[i + 1] == '"':
                        field += '"'
                        i += 2
                    else:
                        in_quotes = False
                        i += 1
                else:
                    field += ch
                    i += 1

        # After exiting inner loop, we are at end of record or EOF
        if not in_quotes:
            rows.append(row)
        else:
            raise ValueError("Unclosed quoted field")

    return rows
