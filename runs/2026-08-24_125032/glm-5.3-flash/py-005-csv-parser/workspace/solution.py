def parse_csv(text: str) -> list[list[str]]:
    """
    Parse CSV text (RFC-4180 style) into a list of records, where each record
    is a list of string fields. Implemented from scratch (no `csv` module).

    - Fields are separated by commas; records by '\
' or '\\r\
'.
    - A field starting with a double quote may contain commas, newlines and
      doubled double-quotes ('""' decodes to one '"').
    - Quotes are only special at the start of a field.
    - Raises ValueError on malformed input (unclosed quote, or unexpected
      characters after a closing quote).
    """
    START, UNQUOTED, QUOTED, AFTER_QUOTE = 0, 1, 2, 3

    records: list[list[str]] = []
    record: list[str] = []
    field_parts: list[str] = []
    state = START
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if state == QUOTED:
            # Inside a quoted field: everything is literal except '"' which
            # either escapes itself ('""') or closes the field.
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_parts.append('"')
                    i += 2
                else:
                    state = AFTER_QUOTE
                    i += 1
            else:
                field_parts.append(c)
                i += 1

        elif state == AFTER_QUOTE:
            # Immediately after a closing quote: only ',', '
', '\r
' or
            # EOF may follow; anything else is malformed.
            if c == ',':
                record.append(''.join(field_parts))
                field_parts = []
                state = START
                i += 1
            elif c == '
':
                record.append(''.join(field_parts))
                records.append(record)
                record = []
                field_parts = []
                state = START
                i += 1
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '
':
                    i += 2
                    record.append(''.join(field_parts))
                    records.append(record)
                    record = []
                    field_parts = []
                    state = START
                else:
                    raise ValueError(
                        "malformed CSV: unexpected character after closing quote"
                    )
            else:
                raise ValueError(
                    "malformed CSV: unexpected character after closing quote"
                )

        else:  # START or UNQUOTED
            if c == ',':
                record.append(''.join(field_parts))
                field_parts = []
                state = START
                i += 1
            elif c == '
':
                record.append(''.join(field_parts))
                records.append(record)
                record = []
                field_parts = []
                state = START
                i += 1
            elif c == '\r':
                if i + 1 < n and text[i + 1] == '
':
                    i += 2
                    record.append(''.join(field_parts))
                    records.append(record)
                    record = []
                    field_parts = []
                    state = START
                else:
                    # A lone '\r' is not a record separator; treat as data.
                    field_parts.append(c)
                    state = UNQUOTED
                    i += 1
            elif c == '"' and state == START:
                # Quote only has special meaning at the start of a field.
                state = QUOTED
                i += 1
            else:
                field_parts.append(c)
                state = UNQUOTED
                i += 1

    # End of input.
    if state == QUOTED:
        raise ValueError("malformed CSV: unclosed quote")
    if state == AFTER_QUOTE:
        # Input ended right after a closing quote: finalize field and record.
        record.append(''.join(field_parts))
        records.append(record)
    elif state == UNQUOTED or record:
        # Finalize pending field/record (handles trailing comma and last
        # line without newline). A trailing newline leaves nothing pending,
        # so it does not create an extra record.
        record.append(''.join(field_parts))
        records.append(record)

    return records
