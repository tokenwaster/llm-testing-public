"""solution.py

CSV parser compliant with RFC‑4180 (subset) without using the built‑in csv module.

Public API
----------
parse_csv(text: str) -> List[List[str]]
    Parse *text* as a CSV document and return a list of records, each a list of
    field strings.

The implementation follows the specification given in the problem statement.
"""

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """
    Parse a CSV string according to RFC‑4180‑style rules described in the prompt.

    Parameters
    ----------
    text : str
        The raw CSV data.

    Returns
    -------
    List[List[str]]
        Parsed rows; each row is a list of field values.

    Raises
    ------
    ValueError
        If the input contains malformed quoting.
    """
    if text == "":
        return []

    n = len(text)
    i = 0                     # current position in the input
    rows: List[List[str]] = []
    cur_row: List[str] = []

    def _peek() -> str | None:
        """Return the current character or None if at EOF."""
        return text[i] if i < n else None

    while i < n:
        ch = _peek()

        # ---------- QUOTED FIELD ----------
        if ch == '"':
            i += 1                       # consume opening quote
            field_chars: List[str] = []
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    # Look ahead for escaped quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2          # consume both quotes
                        continue
                    else:
                        i += 1          # consume closing quote
                        break           # end of quoted field
                else:
                    field_chars.append(c)
                    i += 1
            field_value = "".join(field_chars)

            # After a quoted field only ',', '\n', '\r' or EOF are legal
            next_c = _peek()
            if next_c == ",":
                cur_row.append(field_value)
                i += 1                   # consume comma, move to next field
                continue
            elif next_c == "\r":
                # Handle possible CRLF
                if i + 1 < n and text[i + 1] == "\n":
                    i += 2
                else:
                    i += 1
                cur_row.append(field_value)
                rows.append(cur_row)
                cur_row = []
                continue
            elif next_c == "\n":
                i += 1
                cur_row.append(field_value)
                rows.append(cur_row)
                cur_row = []
                continue
            elif next_c is None:
                # End of input – finalize the current row later
                cur_row.append(field_value)
                i = n
                break
            else:
                raise ValueError(
                    f"Invalid character '{next_c}' after closing quote"
                )

        # ---------- UNQUOTED FIELD ----------
        else:
            start = i
            while i < n and text[i] not in {",", "\n", "\r"}:
                i += 1
            field_value = text[start:i]
            cur_row.append(field_value)

            if i >= n:
                break

            delim = text[i]

            if delim == ",":
                i += 1               # move past the comma, next field follows
                continue
            elif delim == "\r":
                # Possible CRLF
                if i + 1 < n and text[i + 1] == "\n":
                    i += 2
                else:
                    i += 1
                rows.append(cur_row)
                cur_row = []
                continue
            elif delim == "\n":
                i += 1
                rows.append(cur_row)
                cur_row = []
                continue

    # Append the final row if there is any pending data.
    if cur_row:
        rows.append(cur_row)

    return rows
