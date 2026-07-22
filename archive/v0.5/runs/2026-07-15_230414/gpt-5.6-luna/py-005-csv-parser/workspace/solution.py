def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    n = len(text)
    i = 0

    while i < n:
        row: list[str] = []

        while True:
            # An empty field before a newline or at EOF.
            if i == n:
                row.append("")
                rows.append(row)
                break

            if text[i] == "\n":
                row.append("")
                i += 1
                rows.append(row)
                break

            if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                row.append("")
                i += 2
                rows.append(row)
                break

            if text[i] == '"':
                i += 1
                chars: list[str] = []

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
                        chars.append(text[i])
                        i += 1

                field = "".join(chars)
            else:
                start = i
                while i < n:
                    if text[i] == "," or text[i] == "\n":
                        break
                    if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                        break
                    i += 1
                field = text[start:i]

            row.append(field)

            if i == n:
                rows.append(row)
                break

            if text[i] == ",":
                i += 1
                continue

            if text[i] == "\n":
                i += 1
                rows.append(row)
                break

            if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                rows.append(row)
                break

            raise ValueError("invalid characters after closing quote")

    return rows
