def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows = []
    i = 0
    n = len(text)

    while i < n:
        row = []

        while True:
            if text[i] == '"':
                i += 1
                chars = []

                while True:
                    if i >= n:
                        raise ValueError("unterminated quoted field")

                    if text[i] != '"':
                        chars.append(text[i])
                        i += 1
                        continue

                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                        continue

                    i += 1
                    break

                field = "".join(chars)

                if i < n and text[i] == ",":
                    row.append(field)
                    i += 1
                    if i == n:
                        row.append("")
                        rows.append(row)
                        return rows
                    continue

                if i < n and text[i] == "\n":
                    row.append(field)
                    rows.append(row)
                    i += 1
                    break

                if i < n and text[i] == "\r":
                    if i + 1 >= n or text[i + 1] != "\n":
                        raise ValueError("invalid character after closing quote")
                    row.append(field)
                    rows.append(row)
                    i += 2
                    break

                row.append(field)
                rows.append(row)
                return rows

            else:
                start = i
                while i < n and text[i] not in ",\n":
                    i += 1
                field = text[start:i]

                if i < n and text[i] == ",":
                    row.append(field)
                    i += 1
                    if i == n:
                        row.append("")
                        rows.append(row)
                        return rows
                    continue

                row.append(field)

                if i < n and text[i] == "\n":
                    rows.append(row)
                    i += 1
                    break

                rows.append(row)
                return rows

        if i == n:
            break

    return rows
