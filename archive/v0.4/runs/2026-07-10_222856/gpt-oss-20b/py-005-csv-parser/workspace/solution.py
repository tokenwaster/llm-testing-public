#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data and return a list of records,
    each record being a list of fields.

    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    rows = []
    field_chars = []
    row = []
    i = 0
    n = len(text)

    # Helper to add current field to the row
    def finish_field():
        nonlocal field_chars, row
        row.append("".join(field_chars))
        field_chars = []

    while i < n:
        ch = text[i]

        if ch == '"':
            # Start of quoted field
            i += 1
            while i < n:
                c = text[i]
                if c == '"':
                    # Possible end or escaped quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # End of quoted field
                        i += 1
                        break
                else:
                    field_chars.append(c)
                    i += 1
            else:
                # EOF reached without closing quote
                raise ValueError("Unclosed quoted field")

            # After a quoted field, next char must be comma, newline or EOF
            if i < n and text[i] not in {',', '\n'}:
                # Allow \r\n: if it's \r followed by \n we treat as newline
                if text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                    pass
                else:
                    raise ValueError(f"Invalid character after closing quote at position {i}: '{text[i]}'")
            # Finish field
            finish_field()
            # If comma, continue to next field; if newline, finish row
            if i < n and text[i] == ',':
                i += 1
                continue
            elif i < n and text[i] == '\n':
                rows.append(row)
                row = []
                i += 1
                continue
            elif i < n and text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                rows.append(row)
                row = []
                i += 2
                continue
            else:
                # EOF after quoted field
                rows.append(row)
                row = []
                break

        elif ch == ',':
            finish_field()
            i += 1
            continue

        elif ch == '\n':
            finish_field()
            rows.append(row)
            row = []
            i += 1
            continue

        elif ch == '\r':
            # Handle CRLF as a single newline
            if i + 1 < n and text[i + 1] == '\n':
                finish_field()
                rows.append(row)
                row = []
                i += 2
                continue
            else:
                # Lone \r is treated as newline per RFC-4180? We'll treat it similarly.
                finish_field()
                rows.append(row)
                row = []
                i += 1
                continue

        else:
            field_chars.append(ch)
            i += 1

    # After loop, if we have unfinished field or row
    if field_chars or row:
        finish_field()
        rows.append(row)

    # Remove trailing empty record caused by final newline
    if rows and all(len(r) == 0 for r in [rows[-1]]):
        # But an empty line in the middle should produce a single empty field.
        # So we only drop if it was due to trailing newline with no content.
        if len(rows[-1]) == 0:
            rows.pop()

    return rows
