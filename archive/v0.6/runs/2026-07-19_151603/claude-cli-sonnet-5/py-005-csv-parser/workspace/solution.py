def _parse_field(text: str, i: int) -> tuple[str, int]:
    n = len(text)
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
                else:
                    i += 1
                    break
            else:
                chars.append(c)
                i += 1
        if i < n and text[i] not in (',', '\n', '\r'):
            raise ValueError(
                f"Unexpected character after closing quote at position {i}"
            )
        return ''.join(chars), i
    else:
        chars = []
        while i < n and text[i] not in (',', '\n', '\r'):
            chars.append(text[i])
            i += 1
        return ''.join(chars), i


def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    i = 0
    n = len(text)

    while True:
        field, i = _parse_field(text, i)
        record.append(field)

        if i >= n:
            records.append(record)
            break

        c = text[i]
        if c == ',':
            i += 1
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
        elif c == '\n':
            i += 1
            records.append(record)
            record = []
            if i >= n:
                break
            continue

    return records
