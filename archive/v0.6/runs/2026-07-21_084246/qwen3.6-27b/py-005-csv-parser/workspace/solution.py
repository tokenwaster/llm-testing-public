def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    FIELD_START = 0
    IN_UNQUOTED = 1
    IN_QUOTED = 2
    QUOTE_SEEN = 3

    state = FIELD_START
    records = []
    current_record = []
    current_field = []

    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if state == FIELD_START:
            if c == '"':
                state = IN_QUOTED
                i += 1
            elif c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            elif c == '\n' or c == '\r':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
                if c == '\r' and i < n and text[i] == '\n':
                    i += 1
            else:
                current_field.append(c)
                state = IN_UNQUOTED
                i += 1

        elif state == IN_UNQUOTED:
            if c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = FIELD_START
                i += 1
            elif c == '\n' or c == '\r':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
                if c == '\r' and i < n and text[i] == '\n':
                    i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == IN_QUOTED:
            if c == '"':
                state = QUOTE_SEEN
                i += 1
            else:
                current_field.append(c)
                i += 1

        elif state == QUOTE_SEEN:
            if c == '"':
                current_field.append('"')
                state = IN_QUOTED
                i += 1
            elif c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = FIELD_START
                i += 1
            elif c == '\n' or c == '\r':
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
                if c == '\r' and i < n and text[i] == '\n':
                    i += 1
            else:
                raise ValueError("Invalid character after closing quote")

    if state in (IN_QUOTED, QUOTE_SEEN):
        raise ValueError("Unclosed quote")

    current_record.append(''.join(current_field))
    if current_record:
        records.append(current_record)

    return records
