def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    i = 0
    at_field_start = True
    in_quotes = False
    after_quote = False

    while i < len(text):
        char = text[i]

        if in_quotes:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                in_quotes = False
                after_quote = True
            else:
                field.append(char)
            i += 1
            continue

        if after_quote:
            if char == ",":
                record.append("".join(field))
                field = []
                at_field_start = True
                after_quote = False
            elif char == "\n":
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                at_field_start = True
                after_quote = False
            elif char == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                at_field_start = True
                after_quote = False
                i += 1
            else:
                raise ValueError("characters after closing quote")
            i += 1
            continue

        if char == '"' and at_field_start:
            in_quotes = True
            at_field_start = False
        elif char == ",":
            record.append("".join(field))
            field = []
            at_field_start = True
        elif char == "\n":
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
            at_field_start = True
        elif char == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
            at_field_start = True
            i += 1
        else:
            field.append(char)
            at_field_start = False

        i += 1

    if in_quotes:
        raise ValueError("unclosed quoted field")

    if not (at_field_start and not field and not record and not after_quote):
        record.append("".join(field))
        records.append(record)

    return records
