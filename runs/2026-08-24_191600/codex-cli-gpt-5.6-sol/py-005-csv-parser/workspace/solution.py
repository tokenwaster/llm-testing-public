def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    state = "unquoted"
    pending_record = False
    i = 0

    while i < len(text):
        char = text[i]
        is_newline = char == "\n" or (
            char == "\r" and i + 1 < len(text) and text[i + 1] == "\n"
        )
        newline_length = 2 if char == "\r" and is_newline else 1

        if state == "quoted":
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = "after_quote"
                    i += 1
            else:
                field.append(char)
                pending_record = True
                i += 1
            continue

        if state == "after_quote":
            if char == ",":
                record.append("".join(field))
                field = []
                state = "unquoted"
                pending_record = True
                i += 1
            elif is_newline:
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                state = "unquoted"
                pending_record = False
                i += newline_length
            else:
                raise ValueError("unexpected character after closing quote")
            continue

        if char == ",":
            record.append("".join(field))
            field = []
            pending_record = True
            i += 1
        elif is_newline:
            record.append("".join(field))
            records.append(record)
            record = []
            field = []
            pending_record = False
            i += newline_length
        elif char == '"' and not field:
            state = "quoted"
            pending_record = True
            i += 1
        else:
            field.append(char)
            pending_record = True
            i += 1

    if state == "quoted":
        raise ValueError("unclosed quoted field")

    if pending_record:
        record.append("".join(field))
        records.append(record)

    return records
