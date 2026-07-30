def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    current_record: list[str] = []
    field_chars: list[str] = []

    # States
    START_FIELD = "START_FIELD"
    IN_UNQUOTED = "IN_UNQUOTED"
    IN_QUOTED = "IN_QUOTED"
    AFTER_QUOTED = "AFTER_QUOTED"

    state = START_FIELD
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if state == START_FIELD:
            if c == '"':
                state = IN_QUOTED
                i += 1
            elif c == ',':
                # Empty field
                current_record.append("")
                i += 1
            elif c == '\n':
                # Empty field and end of record
                current_record.append("")
                records.append(current_record)
                current_record = []
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                # Empty field and end of record (CRLF)
                current_record.append("")
                records.append(current_record)
                current_record = []
                i += 2
            else:
                # Start of an unquoted field
                field_chars.append(c)
                state = IN_UNQUOTED
                i += 1

        elif state == IN_UNQUOTED:
            if c == ',':
                current_record.append("".join(field_chars))
                field_chars = []
                state = START_FIELD
                i += 1
            elif c == '\n':
                current_record.append("".join(field_chars))
                field_chars = []
                records.append(current_record)
                current_record = []
                state = START_FIELD
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(field_chars))
                field_chars = []
                records.append(current_record)
                current_record = []
                state = START_FIELD
                i += 2
            else:
                field_chars.append(c)
                i += 1

        elif state == IN_QUOTED:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped quote
                    field_chars.append('"')
                    i += 2
                else:
                    # Closing quote
                    state = AFTER_QUOTED
                    i += 1
            else:
                field_chars.append(c)
                i += 1

        elif state == AFTER_QUOTED:
            # After a closing quote we must see a comma, newline, CRLF, or EOF
            if c == ',':
                current_record.append("".join(field_chars))
                field_chars = []
                state = START_FIELD
                i += 1
            elif c == '\n':
                current_record.append("".join(field_chars))
                field_chars = []
                records.append(current_record)
                current_record = []
                state = START_FIELD
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(field_chars))
                field_chars = []
                records.append(current_record)
                current_record = []
                state = START_FIELD
                i += 2
            else:
                raise ValueError("Invalid character after closing quote")

        else:
            # Should never happen
            raise RuntimeError("Invalid parser state")

    # End of input handling
    if state == IN_UNQUOTED:
        current_record.append("".join(field_chars))
        records.append(current_record)
    elif state == IN_QUOTED:
        raise ValueError("Unclosed quoted field")
    elif state == AFTER_QUOTED:
        current_record.append("".join(field_chars))
        records.append(current_record)
    elif state == START_FIELD:
        if current_record:
            # Trailing comma implies an extra empty field
            current_record.append("")
            records.append(current_record)
        # else: input ended right after a record terminator, nothing to add

    return records
