def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    state = "start"
    i = 0

    while i < len(text):
        char = text[i]

        if state == "quoted":
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = "closed"
                    i += 1
            else:
                field.append(char)
                i += 1
            continue

        newline_length = 0
        if char == "\n":
            newline_length = 1
        elif char == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
            newline_length = 2

        if state == "closed":
            if char == ",":
                record.append("".join(field))
                field = []
                state = "start"
                i += 1
            elif newline_length:
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                state = "start"
                i += newline_length
            else:
                raise ValueError("unexpected character after closing quote")
            continue

        if newline_length:
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
            state = "start"
            i += newline_length
        elif char == ",":
            record.append("".join(field))
            field = []
            state = "start"
            i += 1
        elif state == "start" and char == '"':
            state = "quoted"
            i += 1
        else:
            field.append(char)
            state = "unquoted"
            i += 1

    if state == "quoted":
        raise ValueError("unclosed quoted field")

    if state != "start" or field or record or text[-1] == ",":
        record.append("".join(field))
        records.append(record)

    return records
