def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    i = 0
    n = len(text)
    records = []
    record = []

    while True:
        if i < n and text[i] == '"':
            i += 1
            field_chars = []
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                        continue
                    else:
                        i += 1
                        break
                else:
                    field_chars.append(c)
                    i += 1
            record.append(''.join(field_chars))

            if i >= n:
                records.append(record)
                return records

            c = text[i]
            if c == ',':
                i += 1
                continue
            elif c == '\n':
                i += 1
                records.append(record)
                record = []
                if i >= n:
                    return records
                continue
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                i += 2
                records.append(record)
                record = []
                if i >= n:
                    return records
                continue
            else:
                raise ValueError("unexpected character after closing quote")
        else:
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            record.append(''.join(field_chars))

            if i >= n:
                records.append(record)
                return records

            c = text[i]
            if c == ',':
                i += 1
                continue
            elif c == '\n':
                i += 1
                records.append(record)
                record = []
                if i >= n:
                    return records
                continue
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                records.append(record)
                record = []
                if i >= n:
                    return records
                continue
