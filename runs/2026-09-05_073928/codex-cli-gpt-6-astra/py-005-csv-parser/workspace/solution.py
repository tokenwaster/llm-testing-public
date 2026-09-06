def parse_csv(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    i = 0
    n = len(text)

    while i < n:
        row: list[str] = []

        while True:
            field: list[str] = []

            if i < n and text[i] == '"':
                i += 1
                while True:
                    if i >= n:
                        raise ValueError("Unclosed quoted field")
                    if text[i] == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            field.append('"')
                            i += 2
                        else:
                            i += 1
                            break
                    else:
                        field.append(text[i])
                        i += 1

                if (
                    i < n
                    and text[i] not in ",\n"
                    and not text.startswith("\r\n", i)
                ):
                    raise ValueError("Invalid character after closing quote")
            else:
                while (
                    i < n
                    and text[i] not in ",\n"
                    and not text.startswith("\r\n", i)
                ):
                    field.append(text[i])
                    i += 1

            row.append("".join(field))

            if i == n:
                rows.append(row)
                return rows

            if text[i] == ",":
                i += 1
                continue

            # The remaining delimiter is LF or CRLF.
            i += 2 if text[i] == "\r" else 1
            rows.append(row)
            break

    return rows
