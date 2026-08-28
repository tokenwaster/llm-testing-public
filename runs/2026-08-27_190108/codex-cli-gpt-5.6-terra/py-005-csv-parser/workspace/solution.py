def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)
    quoted = False
    after_quote = False

    while i < n:
        char = text[i]

        if quoted:
            if char == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                quoted = False
                after_quote = True
            else:
                field.append(char)
            i += 1
            continue

        if after_quote:
            if char == ",":
                record.append("".join(field))
                field = []
                after_quote = False
                i += 1
                continue
            if char == "\n":
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                after_quote = False
                i += 1
                continue
            if char == "\r" and i + 1 < n and text[i + 1] == "\n":
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                after_quote = False
                i += 2
                continue
            raise ValueError("characters after closing quote")

        if char == '"' and not field:
            quoted = True
        elif char == ",":
            record.append("".join(field))
            field = []
        elif char == "\n":
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
        elif char == "\r" and i + 1 < n and text[i + 1] == "\n":
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
            i += 1
        else:
            field.append(char)

        i += 1

    if quoted:
        raise ValueError("unterminated quoted field")

    if after_quote or field or record or text[-1] not in "\n":
        record.append("".join(field))
        records.append(record)

    return records
