def parse_csv(text: str) -> list[list[str]]:
    n = len(text)
    if n == 0:
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    i = 0

    def newline_len(pos: int) -> int:
        if pos >= n:
            return 0
        if text[pos] == "\n":
            return 1
        if text[pos] == "\r" and pos + 1 < n and text[pos + 1] == "\n":
            return 2
        return 0

    while i < n:
        if text[i] == '"':
            i += 1
            chars: list[str] = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        closed = True
                        break
                else:
                    chars.append(text[i])
                    i += 1
            if not closed:
                raise ValueError("unclosed quoted field")
            if i < n and text[i] != "," and newline_len(i) == 0:
                raise ValueError("unexpected characters after quoted field")
            row.append("".join(chars))
        else:
            start = i
            while i < n and text[i] != "," and newline_len(i) == 0:
                i += 1
            row.append(text[start:i])

        if i >= n:
            rows.append(row)
            break
        if text[i] == ",":
            i += 1
            if i >= n:
                row.append("")
                rows.append(row)
                break
        else:
            i += newline_len(i)
            rows.append(row)
            row = []

    return rows
