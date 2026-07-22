def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []

    state = "start"  # start, unquoted, quoted, after_quote
    record_active = False
    i = 0
    n = len(text)

    def finish_record() -> None:
        nonlocal record, field
        record.append("".join(field))
        records.append(record)
        record = []
        field = []

    while i < n:
        ch = text[i]

        if state == "quoted":
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = "after_quote"
                    i += 1
            else:
                field.append(ch)
                i += 1
            continue

        if state == "after_quote":
            if ch == ",":
                record.append("".join(field))
                field = []
                state = "start"
                record_active = True
                i += 1
            elif ch == "\n":
                finish_record()
                state = "start"
                record_active = False
                i += 1
            elif ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                finish_record()
                state = "start"
                record_active = False
                i += 2
            else:
                raise ValueError("characters after closing quote")
            continue

        if state == "start":
            if ch == '"':
                state = "quoted"
                record_active = True
                i += 1
            elif ch == ",":
                record.append("")
                record_active = True
                i += 1
            elif ch == "\n":
                finish_record()
                record_active = False
                i += 1
            elif ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                finish_record()
                record_active = False
                i += 2
            else:
                field.append(ch)
                state = "unquoted"
                record_active = True
                i += 1
            continue

        # state == "unquoted"
        if ch == ",":
            record.append("".join(field))
            field = []
            state = "start"
            record_active = True
            i += 1
        elif ch == "\n":
            finish_record()
            state = "start"
            record_active = False
            i += 1
        elif ch == "\r" and i + 1 < n and text[i + 1] == "\n":
            finish_record()
            state = "start"
            record_active = False
            i += 2
        else:
            field.append(ch)
            i += 1

    if state == "quoted":
        raise ValueError("unterminated quoted field")

    if record_active:
        record.append("".join(field))
        records.append(record)

    return records
