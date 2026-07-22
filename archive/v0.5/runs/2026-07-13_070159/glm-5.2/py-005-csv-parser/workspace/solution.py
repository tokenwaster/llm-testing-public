def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    current_record: list[str] = []
    current_field: list[str] = []
    i = 0
    n = len(text)

    # states: 0=start of field, 1=unquoted, 2=quoted, 3=quote seen inside quoted
    state = 0

    while i < n:
        c = text[i]

        if state == 0:
            if c == '"':
                state = 2
                i += 1
            elif c == ',':
                current_record.append("")
                i += 1
            elif c == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 2
            else:
                current_field.append(c)
                state = 1
                i += 1

        elif state == 1:
            if c == ',':
                current_record.append("".join(current_field))
                current_field = []
                state = 0
                i += 1
            elif c == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 0
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 0
                i += 2
            else:
                current_field.append(c)
                i += 1

        elif state == 2:
            if c == '"':
                state = 3
                i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == 3:
            if c == '"':
                current_field.append('"')
                state = 2
                i += 1
            elif c == ',':
                current_record.append("".join(current_field))
                current_field = []
                state = 0
                i += 1
            elif c == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 0
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 0
                i += 2
            else:
                raise ValueError("Malformed CSV: unexpected character after closing quote")

    if state == 2:
        raise ValueError("Malformed CSV: unterminated quoted field")

    if state == 0:
        # End of input at a field boundary.
        # If the last consumed character was a newline, current_record is empty
        # and we should not emit an extra record. Otherwise (last was a comma),
        # we need to close the current record with an empty field.
        if current_record or current_field:
            current_record.append("".join(current_field))
            records.append(current_record)
    else:
        current_record.append("".join(current_field))
        records.append(current_record)

    return records
