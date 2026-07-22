def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == '"':
            i += 1
            parts: list[str] = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        parts.append('"')
                        i += 2
                    else:
                        i += 1
                        closed = True
                        break
                else:
                    parts.append(text[i])
                    i += 1
            if not closed:
                raise ValueError("unclosed quote")
            field = "".join(parts)
            if i < n and text[i] not in (",", "\n", "\r"):
                raise ValueError("unexpected data after closing quote")
        else:
            start = i
            while i < n and text[i] not in (",", "\n", "\r"):
                i += 1
            field = text[start:i]

        row.append(field)

        if i >= n:
            rows.append(row)
            break
        if text[i] == ",":
            i += 1
            if i >= n:
                row.append("")
                rows.append(row)
                break
        elif text[i] == "\r":
            i += 1
            if i < n and text[i] == "\n":
                i += 1
            rows.append(row)
            row = []
            if i >= n:
                break
        elif text[i] == "\n":
            i += 1
            rows.append(row)
            row = []
            if i >= n:
                break
        else:
            raise ValueError("unexpected character")

    return rows
