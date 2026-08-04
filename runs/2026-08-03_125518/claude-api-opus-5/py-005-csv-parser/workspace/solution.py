"""RFC-4180-style CSV parser written from scratch.

No use of the ``csv`` module or any other parsing library.
"""

from typing import List


def parse_csv(text: str) -> List[List[str]]:
    """Parse ``text`` as RFC-4180-style CSV and return a list of records.

    Each record is a list of decoded field strings.

    Raises:
        ValueError: on malformed input (unterminated quoted field, or stray
            characters following a closing quote).
    """
    if not isinstance(text, str):
        raise TypeError("parse_csv expects a str")

    n = len(text)
    if n == 0:
        return []

    rows: List[List[str]] = []
    row: List[str] = []
    i = 0

    while i < n:
        # ---- parse one field -------------------------------------------
        if text[i] == '"':
            i += 1
            chars: List[str] = []
            closed = False
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                        continue
                    i += 1
                    closed = True
                    break
                if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    chars.append('\n')
                    i += 2
                    continue
                chars.append(ch)
                i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            field = ''.join(chars)

            # after a closing quote only , \n \r\n or EOF may follow
            if i < n:
                ch = text[i]
                if ch == ',':
                    pass  # handled below
                elif ch == '\n':
                    pass
                elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    pass
                else:
                    raise ValueError(
                        "unexpected character after closing quote: %r" % ch
                    )
        else:
            start = i
            while i < n:
                ch = text[i]
                if ch == ',' or ch == '\n':
                    break
                if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    break
                i += 1
            field = text[start:i]

        row.append(field)

        # ---- consume the delimiter / record separator -------------------
        if i >= n:
            rows.append(row)
            row = []
            break

        ch = text[i]
        if ch == ',':
            i += 1
            if i >= n:
                # trailing comma: an empty final field, then end of input
                row.append('')
                rows.append(row)
                row = []
            continue
        if ch == '\n':
            i += 1
        elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
            i += 2
        else:  # pragma: no cover - defensive
            raise ValueError("unexpected character: %r" % ch)

        rows.append(row)
        row = []

    if row:  # pragma: no cover - defensive
        rows.append(row)

    return rows
