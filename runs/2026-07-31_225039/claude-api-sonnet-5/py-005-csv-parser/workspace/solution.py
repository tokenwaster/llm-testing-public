def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)
    i = 0
    records: list[list[str]] = []
    record: list[str] = []

    def parse_field() -> str:
        nonlocal i
        if i < n and text[i] == '"':
            i += 1
            chars = []
            while True:
                if i >= n:
                    raise ValueError("Unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                        continue
                    else:
                        i += 1
                        break
                else:
                    chars.append(c)
                    i += 1
            # After the closing quote, only comma, newline, or EOF are allowed.
            if i < n:
                c = text[i]
                if c not in (',', '\n', '\r'):
                    raise ValueError(
                        "Unexpected characters after closing quote"
                    )
            return ''.join(chars)
        else:
            chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                chars.append(text[i])
                i += 1
            return ''.join(chars)

    while True:
        field = parse_field()
        record.append(field)

        if i >= n:
            records.append(record)
            break

        c = text[i]
        if c == ',':
            i += 1
            continue
        elif c == '\n':
            i += 1
            records.append(record)
            record = []
            if i >= n:
                break
            continue
        elif c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            records.append(record)
            record = []
            if i >= n:
                break
            continue
        else:
            # Should not happen: unquoted fields stop only at ',', '\n', '\r',
            # and quoted fields already validate the trailing character.
            raise ValueError("Unexpected character in input")

    return records
