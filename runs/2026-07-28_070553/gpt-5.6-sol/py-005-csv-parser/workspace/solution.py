def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []

    START_FIELD = 0
    UNQUOTED = 1
    QUOTED = 2
    AFTER_QUOTE = 3

    state = START_FIELD
    record_active = False
    i = 0

    while i < len(text):
        char = text[i]
        is_newline = char == "\n" or (
            char == "\r" and i + 1 < len(text) and text[i + 1] == "\n"
        )

        if state == START_FIELD:
            if char == ",":
                record.append("")
                record_active = True
                i += 1
            elif is_newline:
                record.append("")
                records.append(record)
                record = []
                record_active = False
                i += 2 if char == "\r" else 1
            elif char == '"':
                state = QUOTED
                record_active = True
                i += 1
            else:
                field.append(char)
                state = UNQUOTED
                record_active = True
                i += 1

        elif state == UNQUOTED:
            if char == ",":
                record.append("".join(field))
                field = []
                state = START_FIELD
                i += 1
            elif is_newline:
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                state = START_FIELD
                record_active = False
                i += 2 if char == "\r" else 1
            else:
                field.append(char)
                i += 1

        elif state == QUOTED:
            if char == '"':
                if i + 1 < len(text) and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                field.append(char)
                i += 1

        else:  # AFTER_QUOTE
            if char == ",":
                record.append("".join(field))
                field = []
                state = START_FIELD
                i += 1
            elif is_newline:
                record.append("".join(field))
                records.append(record)
                record = []
                field = []
                state = START_FIELD
                record_active = False
                i += 2 if char == "\r" else 1
            else:
                raise ValueError("unexpected character after closing quote")

    if state == QUOTED:
        raise ValueError("unterminated quoted field")

    if record_active:
        record.append("".join(field))
        records.append(record)

    return records
