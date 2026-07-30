def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    i = 0
    n = len(text)

    def is_newline_at(pos: int) -> bool:
        return (
            pos < n
            and (
                text[pos] == "\n"
                or (text[pos] == "\r" and pos + 1 < n and text[pos + 1] == "\n")
            )
        )

    while True:
        if i < n and text[i] == '"':
            i += 1
            value: list[str] = []
            closed = False

            while i < n:
                char = text[i]

                if char == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        value.append('"')
                        i += 2
                    else:
                        i += 1
                        closed = True
                        break
                elif char == "\r" and i + 1 < n and text[i + 1] == "\n":
                    value.append("\r\n")
                    i += 2
                else:
                    value.append(char)
                    i += 1

            if not closed:
                raise ValueError("Unclosed quoted field")

            if i < n:
                if text[i] == "," or text[i] == "\n":
                    pass
                elif text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                    pass
                else:
                    raise ValueError("Invalid character after closing quote")

            field = "".join(value)
        else:
            start = i
            while i < n and text[i] != "," and not is_newline_at(i):
                i += 1
            field = text[start:i]

        fields.append(field)

        if i >= n:
            records.append(fields)
            break

        if text[i] == ",":
            i += 1
            continue

        if text[i] == "\n":
            i += 1
        else:
            i += 2  # CRLF

        records.append(fields)
        fields = []

        if i >= n:
            break

    return records
