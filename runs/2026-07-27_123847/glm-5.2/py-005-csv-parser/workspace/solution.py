def parse_csv(text: str) -> list[list[str]]:
    records: list[list[str]] = []
    record: list[str] = []
    field_chars: list[str] = []
    state = "START"          # START, UNQUOTED, QUOTED, AFTER_QUOTE
    i = 0
    n = len(text)

    if n == 0:
        return []

    while i < n:
        ch = text[i]

        if state == "START":
            if ch == '"':
                state = "QUOTED"
                i += 1
            elif ch == ',':
                record.append("")
                state = "START"
                i += 1
            elif ch == '\n':
                record.append("")
                records.append(record)
                record = []
                state = "START"
                i += 1
            elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                record.append("")
                records.append(record)
                record = []
                state = "START"
                i += 2
            else:
                field_chars.append(ch)
                state = "UNQUOTED"
                i += 1

        elif state == "UNQUOTED":
            if ch == ',':
                record.append("".join(field_chars))
                field_chars = []
                state = "START"
                i += 1
            elif ch == '\n':
                record.append("".join(field_chars))
                field_chars = []
                records.append(record)
                record = []
                state = "START"
                i += 1
            elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                record.append("".join(field_chars))
                field_chars = []
                records.append(record)
                record = []
                state = "START"
                i += 2
            else:
                field_chars.append(ch)
                i += 1

        elif state == "QUOTED":
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')
                    i += 2
                else:
                    state = "AFTER_QUOTE"
                    i += 1
            else:
                field_chars.append(ch)
                i += 1

        else:  # state == "AFTER_QUOTE"
            if ch == ',':
                record.append("".join(field_chars))
                field_chars = []
                state = "START"
                i += 1
            elif ch == '\n':
                record.append("".join(field_chars))
                field_chars = []
                records.append(record)
                record = []
                state = "START"
                i += 1
            elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                record.append("".join(field_chars))
                field_chars = []
                records.append(record)
                record = []
                state = "START"
                i += 2
            else:
                raise ValueError("unexpected character after closing quote")

    if state == "QUOTED":
        raise ValueError("unterminated quoted field")

    if state == "UNQUOTED" or state == "AFTER_QUOTE":
        record.append("".join(field_chars))
        records.append(record)
    elif state == "START":
        # A pending empty field exists only when a comma was the last separator.
        if record:
            record.append("")
            records.append(record)

    return records
