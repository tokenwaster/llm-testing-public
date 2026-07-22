#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """
    Parse a string containing CSV data and return a list of rows,
    each row being a list of fields.

    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    rows: List[List[str]] = []
    field_chars: List[str] = []
    current_row: List[str] = []

    i = 0
    length = len(text)

    def add_field():
        """Append the accumulated field to the current row."""
        nonlocal field_chars, current_row
        current_row.append("".join(field_chars))
        field_chars = []

    while i < length:
        ch = text[i]

        # Handle quoted field start
        if ch == '"':
            # If we are at the beginning of a field (no preceding chars)
            if not field_chars and (not current_row or current_row[-1] != ""):
                # Consume opening quote
                i += 1
                while i < length:
                    c = text[i]
                    if c == '"':
                        # Check for escaped double-quote
                        if i + 1 < length and text[i + 1] == '"':
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
                    raise ValueError("Unclosed quoted field")

                # After closing quote, next char must be comma, newline or EOF
                if i < length and text[i] not in {',', '\n'}:
                    raise ValueError(f"Invalid character after closing quote at position {i}")
            else:
                # Quote inside unquoted field is literal
                field_chars.append('"')
                i += 1

        elif ch == ',':
            add_field()
            i += 1

        elif ch == '\n':
            add_field()
            rows.append(current_row)
            current_row = []
            i += 1

        elif ch == '\r':
            # Handle CRLF
            if i + 1 < length and text[i + 1] == '\n':
                add_field()
                rows.append(current_row)
                current_row = []
                i += 2
            else:
                # Lone CR treated as newline
                add_field()
                rows.append(current_row)
                current_row = []
                i += 1

        else:
            field_chars.append(ch)
            i += 1

    # End of input: finalize last field and row if any
    add_field()
    if current_row or (rows and rows[-1] != current_row):
        rows.append(current_row)

    # Remove trailing empty record caused by final newline
    if rows and all(len(row) == 1 and row[0] == "" for row in [rows[-1]]):
        # Check if the last line was actually an empty line
        # If input ends with a newline, we should not add an extra empty record
        if text.endswith("\n") or text.endswith("\r\n"):
            rows.pop()

    return rows


# Simple test harness (not part of required output)
if __name__ == "__main__":
    import sys

    sample = 'a,b,c\r\nd,"e,f",g\r\n"h","i""j","k"\n'
    print(parse_csv(sample))
