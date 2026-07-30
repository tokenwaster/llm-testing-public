def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    def is_newline_at(index: int) -> bool:
        return text[index] == "\n" or (
            text[index] == "\r"
            and index + 1 < len(text)
            and text[index + 1] == "\n"
        )

    def consume_newline(index: int) -> int:
        if text[index] == "\r":
            return index + 2
        return index + 1

    records: list[list[str]] = []
    i = 0
    n = len(text)

    while i < n:
        record: list[str] = []

        while True:
            if i < n and text[i] == '"':
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

                if i < n and text[i] != "," and not is_newline_at(i):
                    raise ValueError("invalid character after closing quote")
            else:
                start = i
                while i < n and text[i] != "," and not is_newline_at(i):
                    i += 1
                field = text[start:i]

            record.append(field)

            if i >= n:
                records.append(record)
                break

            if text[i] == ",":
                i += 1
                continue

            if is_newline_at(i):
                i = consume_newline(i)
                records.append(record)
                break

    return records
