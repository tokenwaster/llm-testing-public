"""RFC-4180-style CSV parser written from scratch (no `csv` module)."""


def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of records.

    Fields are comma-separated, records are separated by ``\\n`` or ``\\r\\n``.
    A field that *starts* with a double quote is a quoted field: it may contain
    commas, newlines, and doubled quotes (``""`` -> ``"``).  Quotes elsewhere in
    a field are literal characters.

    Raises:
        ValueError: on an unterminated quoted field, or on stray characters
            after a closing quote.
    """
    if not text:
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

    while True:
        if text[i:i + 1] == '"':
            i += 1
            parts: list[str] = []
            closed = False
            while i < n:
                ch = text[i]
                if ch == '"':
                    if text[i + 1:i + 2] == '"':
                        parts.append('"')
                        i += 2
                        continue
                    i += 1
                    closed = True
                    break
                parts.append(ch)
                i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            value = "".join(parts)
            if i < n:
                nxt = text[i]
                is_sep = (
                    nxt == ","
                    or nxt == "\n"
                    or (nxt == "\r" and text[i + 1:i + 2] == "\n")
                )
                if not is_sep:
                    raise ValueError(
                        "unexpected character after closing quote: %r" % nxt
                    )
        else:
            start = i
            while i < n:
                ch = text[i]
                if ch == "," or ch == "\n":
                    break
                if ch == "\r" and text[i + 1:i + 2] == "\n":
                    break
                i += 1
            value = text[start:i]

        row.append(value)

        if i >= n:
            rows.append(row)
            break

        if text[i] == ",":
            i += 1
            continue

        # Record separator: "\n" or "\r\n".
        i += 2 if text[i] == "\r" else 1
        rows.append(row)
        row = []
        if i >= n:
            break

    return rows
