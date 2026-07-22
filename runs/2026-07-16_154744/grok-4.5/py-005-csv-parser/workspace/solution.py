def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    result: list[list[str]] = []
    row: list[str] = []
    i = 0
    n = len(text)

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
                raise ValueError("unclosed quote")
            field = "".join(chars)
            if i < n and text[i] not in ",\r\n":
                raise ValueError("unexpected characters after closing quote")
        else:
            start = i
            while i < n and text[i] not in ",\r\n":
                i += 1
            field = text[start:i]

        row.append(field)

        if i >= n:
            result.append(row)
            break

        if text[i] == ",":
            i += 1
            if i >= n:
                row.append("")
                result.append(row)
                break
        else:
            if text[i] == "\r":
                i += 1
                if i < n and text[i] == "\n":
                    i += 1
            else:
                i += 1
            result.append(row)
            row = []

    return result
