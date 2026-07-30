def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    i = 0
    n = len(text)

    while True:
        if i < n and text[i] == '"':
            i += 1
            chars: list[str] = []

            while True:
                if i >= n:
                    raise ValueError("unclosed quoted field")

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

            if i < n:
                is_newline = (
                    text[i] == "\n"
                    or (text[i] == "\r" and i + 1 < n and text[i + 1] == "\n")
                )
                if text[i] != "," and not is_newline:
                    raise ValueError("unexpected character after closing quote")
        else:
            start = i
            while i < n:
                if text[i] == "," or text[i] == "\n":
                    break
                if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                i += 1
            field = text[start:i]

        record.append(field)

        if i >= n:
            records.append(record)
            break

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
            break

    return records
