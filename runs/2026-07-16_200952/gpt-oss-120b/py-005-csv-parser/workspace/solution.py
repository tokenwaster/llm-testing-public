# solution.py
from __future__ import annotations

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """
    Parse a CSV string according to a subset of RFC‑4180.

    Rules implemented:
    * Fields are separated by commas, records by LF (``\\n``) or CRLF (``\\r\\n``).
    * A field that starts with a double quote is a *quoted* field.
      Inside a quoted field a double quote is escaped by doubling it (``""`` → ``"``).
      Newlines and commas are allowed inside quoted fields.
    * If a field does not start with a quote, the quote character has no special
      meaning – it is treated as a literal character.
    * Empty fields decode to the empty string.
    * A trailing newline does not create an extra record, but an empty line
      inside the data creates a record containing a single empty field.
    * ``parse_csv("")`` returns ``[]``.
    * Malformed input raises ``ValueError``.
    """
    if text == "":
        return []

    # Normalise line endings: treat CRLF and CR as LF.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    n = len(text)
    i = 0                     # current position in the input
    rows: List[List[str]] = []  # accumulated rows
    row: List[str] = []         # fields of the current row

    while True:
        # ---------- parse a single field ----------
        if i < n and text[i] == '"':
            # Quoted field
            i += 1  # skip opening quote
            field_chars: List[str] = []
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                ch = text[i]
                if ch == '"':
                    # Could be an escaped quote or the closing quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        i += 1  # consume closing quote
                        break
                else:
                    field_chars.append(ch)
                    i += 1
            field = "".join(field_chars)

            # After a quoted field the next character must be a delimiter or EOF
            if i < n and text[i] not in {",", "\n"}:
                raise ValueError("Invalid character after closing quote")
        else:
            # Unquoted field (may be empty)
            start = i
            while i < n and text[i] not in {",", "\n"}:
                i += 1
            field = text[start:i]

        # Add the parsed field to the current row
        row.append(field)

        # ---------- delimiter handling ----------
        if i >= n:
            # End of input – finish the current row
            rows.append(row)
            break

        delim = text[i]
        i += 1  # consume delimiter

        if delim == ",":
            # More fields follow on the same row
            continue
        elif delim == "\n":
            # End of the current record
            rows.append(row)
            row = []
            # If we are at EOF right after the newline, do not create an extra empty row
            if i >= n:
                break
            # otherwise start parsing the next record
            continue
        else:
            # Should never happen because we only split on ',' or '\n'
            raise ValueError("Unexpected delimiter")

    return rows
