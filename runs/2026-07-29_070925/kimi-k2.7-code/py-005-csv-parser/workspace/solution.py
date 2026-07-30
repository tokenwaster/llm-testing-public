def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-like CSV text and return a list of rows.

    Fields are separated by commas and records by ``\\n`` or ``\\r\\n``.
    Quoted fields may contain commas, newlines, and escaped quotes (``""``).
    """
    if not text:
        return []

    records: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

    def parse_field():
        nonlocal i
        if text[i] == '"':
            # Quoted field
            i += 1
            parts: list[str] = []
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        parts.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    parts.append(text[i])
                    i += 1
            else:
                raise ValueError("unterminated quoted field")

            field = "".join(parts)

            if i >= n:
                return field, None
            if text[i] == ",":
                i += 1
                return field, ","
            if text[i] == "\n":
                i += 1
                return field, "\n"
            if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                return field, "\n"
            raise ValueError("extraneous data after closing quote")

        # Unquoted field
        start = i
        while i < n:
            ch = text[i]
            if ch == ",":
                break
            if ch == "\n":
                break
            if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                break
            i += 1

        field = text[start:i]

        if i >= n:
            return field, None
        if text[i] == ",":
            i += 1
            return field, ","
        if text[i] == "\r":
            i += 2
        else:
            i += 1
        return field, "\n"

    while True:
        field, sep = parse_field()
        row.append(field)

        if sep == ",":
            if i == n:
                row.append("")
                records.append(row)
                break
            continue

        if sep == "\n":
            records.append(row)
            row = []
            if i == n:
                break
            continue

        # End of input
        records.append(row)
        break

    return records
