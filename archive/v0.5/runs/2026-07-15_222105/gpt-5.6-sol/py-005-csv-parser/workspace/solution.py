def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    i = 0
    n = len(text)

    def is_newline(pos: int) -> bool:
        return (
            text[pos] == "\n"
            or (
                text[pos] == "\r"
                and pos + 1 < n
                and text[pos + 1] == "\n"
            )
        )

    while True:
        if i < n and text[i] == '"':
            i += 1
            parts: list[str] = []

            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")

                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        parts.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    parts.append(text[i])
                    i += 1

            field = "".join(parts)

            if i < n and text[i] != "," and not is_newline(i):
                raise ValueError("Unexpected character after closing quote")
        else:
            start = i
            while i < n and text[i] != "," and not is_newline(i):
                i += 1
            field = text[start:i]

        record.append(field)

        if i >= n:
            records.append(record)
            return records

        if text[i] == ",":
            i += 1
            continue

        if text[i] == "\r":
            i += 2
        else:
            i += 1

        records.append(record)
        record = []

        if i >= n:
            return records
