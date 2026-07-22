def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)
    i = 0
    records = []
    record = []

    while True:
        if i < n and text[i] == '"':
            i += 1
            chars = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
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
            field = ''.join(chars)
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError("unexpected characters after closing quote")
        else:
            start = i
            while i < n and text[i] not in (',', '\n', '\r'):
                i += 1
            field = text[start:i]

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
        else:  # c == '\r'
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            records.append(record)
            record = []
            if i >= n:
                break
            continue

    return records
