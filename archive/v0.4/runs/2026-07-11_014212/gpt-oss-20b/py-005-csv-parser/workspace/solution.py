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
    i = 0
    n = len(text)

    while i < n:
        # Start parsing a new record
        row = []
        field = ""
        in_quotes = False

        while True:
            if i >= n:
                # End of file: finalize last field and break
                row.append(field)
                rows.append(row)
                return rows

            ch = text[i]

            if not in_quotes:
                if ch == ',':
                    # Field separator
                    row.append(field)
                    field = ""
                    i += 1
                elif ch == '\n':
                    # Record separator (LF only, CR handled below)
                    row.append(field)
                    rows.append(row)
                    field = ""
                    i += 1
                    break
                elif ch == '\r':
                    # Possible CRLF
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    row.append(field)
                    rows.append(row)
                    field = ""
                    break
                elif ch == '"':
                    # Start quoted field
                    in_quotes = True
                    i += 1
                else:
                    # Regular character
                    field += ch
                    i += 1
            else:
                # Inside a quoted field
                if ch == '"':
                    # Could be end of quotes or escaped quote
                    if i + 1 < n and text[i + 1] == '"':
                        # Escaped quote
                        field += '"'
                        i += 2
                    else:
                        # End of quoted field
                        in_quotes = False
                        i += 1
                elif ch == '\n' or ch == '\r':
                    # Newlines inside quotes are allowed
                    if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                        field += '\r\n'
                        i += 2
                    else:
                        field += ch
                        i += 1
                else:
                    field += ch
                    i += 1

        # After finishing a record, check for malformed trailing characters
        if in_quotes:
            raise ValueError("Unclosed quoted field")

    return rows


# Simple test harness (not part of the required output)
if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    try:
        result = parse_csv(data)
        for row in result:
            print(row)
    except ValueError as e:
        sys.exit(str(e))
