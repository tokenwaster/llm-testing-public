def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)
    i = 0
    records: list[list[str]] = []
    row: list[str] = []

    while True:
        if i < n and text[i] == '"':
            i += 1
            chars = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        closed = True
                        i += 1
                        break
                else:
                    chars.append(c)
                    i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            field = "".join(chars)
        else:
            start = i
            while i < n:
                if text[i] in (",", "\n"):
                    break
                if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                i += 1
            field = text[start:i]

        row.append(field)

        if i >= n:
            records.append(row)
            break

        c = text[i]
        if c == ",":
            i += 1
            if i >= n:
                row.append("")
                records.append(row)
                break
            continue
        elif c == "\n":
            records.append(row)
            row = []
            i += 1
            if i >= n:
                break
            continue
        elif c == "\r" and i + 1 < n and text[i + 1] == "\n":
            records.append(row)
            row = []
            i += 2
            if i >= n:
                break
            continue
        else:
            raise ValueError(f"unexpected character after closing quote at position {i}")

    return records
