#!/usr/bin/env python3
"""
RFC-4180 style CSV parser implemented from scratch.
"""

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """
    Parse a string containing CSV data according to RFC‑4180 rules.

    Parameters
    ----------
    text : str
        The input CSV text. May contain ``\n`` or ``\r\n`` line endings.
        A trailing newline does not create an extra record, but an empty
        line in the middle is a record with one empty field.

    Returns
    -------
    List[List[str]]
        A list of rows; each row is a list of fields (strings).

    Raises
    ------
    ValueError
        If the input contains malformed quoted fields or unexpected
        characters after a closing quote.
    """
    if text == "":
        return []

    # Normalise line endings to '\n' for easier processing
    text = text.replace("\r\n", "\n")

    rows: List[List[str]] = []
    field_chars: List[str] = []
    row: List[str] = []

    i = 0
    length = len(text)

    def add_field():
        """Append the current field to the current row."""
        nonlocal field_chars, row
        row.append("".join(field_chars))
        field_chars = []

    while i < length:
        ch = text[i]

        if ch == '"':
            # Start of a quoted field or an escaped quote inside a quoted field
            i += 1
            start_quote = True
            while i < length:
                c = text[i]
                if c == '"':
                    # Check for doubled double-quote
                    if i + 1 < length and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                        continue
                    else:
                        # End of quoted field
                        i += 1
                        start_quote = False
                        break
                else:
                    field_chars.append(c)
                    i += 1

            if start_quote:
                raise ValueError("Unclosed quote in input")

            # After closing quote, next char must be comma, newline or EOF
            if i < length and text[i] not in {',', '\n'}:
                raise ValueError(f"Unexpected character '{text[i]}' after closing quote")
            add_field()
            # If we hit a comma, skip it; if newline, finish row
            if i < length:
                if text[i] == ',':
                    i += 1
                    continue
                elif text[i] == '\n':
                    rows.append(row)
                    row = []
                    i += 1
                    continue

        elif ch == ',':
            add_field()
            i += 1
            continue

        elif ch == '\n':
            # End of record
            add_field()
            rows.append(row)
            row = []
            i += 1
            continue

        else:
            # Unquoted field character
            field_chars.append(ch)
            i += 1
            continue

    # After loop ends, handle last field/row if any
    if field_chars or row:
        add_field()
        rows.append(row)

    return rows


# If run as a script, provide simple demonstration
if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    try:
        result = parse_csv(data)
        for r in result:
            print(r)
    except ValueError as e:
        sys.exit(f"Error parsing CSV: {e}")
