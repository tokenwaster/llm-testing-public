def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    def is_newline_at(pos: int) -> bool:
        return text[pos] == "\n" or (
            text[pos] == "\r" and pos + 1 < len(text) and text[pos + 1] == "\n"
        )

    rows: list[list[str]] = []
    n = len(text)
    i = 0

    while i < n:
        row: list[str] = []

        if text[i] == '"':
            i += 1
            chars: list[str] = []
            closed = False

            while i < n:
                char = text[i]

                if char == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        closed = True
                        break
                elif char == "\r" and i + 1 < n and text[i + 1] == "\n":
                    chars.append("\r\n")
                    i += 2
                else:
                    chars.append(char)
                    i += 1

            if not closed:
                raise ValueError("unterminated quoted field")

            field = "".join(chars)

            if i < n and text[i] != "," and not is_newline_at(i):
                raise ValueError("invalid characters after closing quote")
        else:
            start = i
            while i < n and text[i] != "," and not is_newline_at(i):
                i += 1
            field = text[start:i]

        row.append(field)

        if i == n:
            rows.append(row)
            break

        if text[i] == ",":
            i += 1
            if i == n:
                row.append("")
                rows.append(row)
            continue

        if text[i] == "\n":
            i += 1
        else:
            i += 2  # \r\n

        rows.append(row)

    return rows
