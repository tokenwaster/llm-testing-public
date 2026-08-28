def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows = []
    row = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == '"':
            i += 1
            chars = []

            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")

                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                        chars.append("\r\n")
                        i += 2
                    else:
                        chars.append(text[i])
                        i += 1

            field = "".join(chars)

            if i < n and text[i] not in ",\r\n":
                raise ValueError("invalid character after closing quote")
        else:
            start = i
            while i < n and text[i] not in ",\r\n":
                i += 1
            field = text[start:i]

        row.append(field)

        if i >= n:
            rows.append(row)
            break

        if text[i] == ",":
            i += 1
            continue

        if text[i] == "\n":
            i += 1
        else:
            if i + 1 >= n or text[i + 1] != "\n":
                raise ValueError("invalid carriage return")
            i += 2

        rows.append(row)
        row = []

        if i >= n:
            break

    return rows
