def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of records.

    Implemented from scratch; no parsing libraries are used.
    """
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    i = 0
    n = len(text)

    while True:
        # --- parse one field starting at i ---
        if i < n and text[i] == '"':
            # Quoted field.
            i += 1
            parts: list[str] = []
            closed = False
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
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
            field = "".join(parts)
            # After a closing quote only comma, newline, or EOF may follow.
            if i < n and text[i] not in (",", "\n", "\r"):
                raise ValueError("unexpected character after closing quote")
            if i < n and text[i] == "\r" and not (i + 1 < n and text[i + 1] == "\n"):
                raise ValueError("unexpected character after closing quote")
        else:
            # Unquoted field: runs until comma, newline, or EOF.
            start = i
            while i < n and text[i] != "," and text[i] != "\n" and text[i] != "\r":
                i += 1
            field = text[start:i]
            if i < n and text[i] == "\r" and not (i + 1 < n and text[i + 1] == "\n"):
                # A lone \r is not a record separator; treat it as data.
                field += "\r"
                i += 1
                while True:
                    start = i
                    while i < n and text[i] not in (",", "\n", "\r"):
                        i += 1
                    field += text[start:i]
                    if i < n and text[i] == "\r" and not (
                        i + 1 < n and text[i + 1] == "\n"
                    ):
                        field += "\r"
                        i += 1
                        continue
                    break

        record.append(field)

        # --- decide what follows the field ---
        if i >= n:
            records.append(record)
            break
        if text[i] == ",":
            i += 1
            continue
        # Record separator: \n or \r\n
        if text[i] == "\r":
            i += 2
        else:
            i += 1
        records.append(record)
        record = []
        if i >= n:
            # Trailing newline does not create an extra record.
            break

    return records
