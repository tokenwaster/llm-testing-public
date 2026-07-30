def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records: list[list[str]] = []
    record: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)

    # States:
    #   'field_start'  - at the start of a field (or just after a separator/newline)
    #   'unquoted'     - reading an unquoted field
    #   'quoted'       - inside a quoted field
    #   'quoted_end'   - closing quote was just seen; need , or newline or EOF
    state = 'field_start'
    pending = False  # True if we have partial record content since last newline

    def end_field() -> None:
        nonlocal record, field
        record.append(''.join(field))
        field = []

    def end_record() -> None:
        nonlocal record, records
        records.append(record)
        record = []

    def handle_newline() -> None:
        end_field()
        end_record()

    while i < n:
        c = text[i]
        if state == 'field_start':
            if c == '"':
                state = 'quoted'
                pending = True
                i += 1
            elif c == ',':
                end_field()
                pending = True
                i += 1
            elif c == '\n':
                handle_newline()
                pending = False
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                handle_newline()
                pending = False
                i += 2
            else:
                state = 'unquoted'
                field.append(c)
                pending = True
                i += 1
        elif state == 'unquoted':
            if c == ',':
                end_field()
                pending = True
                state = 'field_start'
                i += 1
            elif c == '\n':
                handle_newline()
                pending = False
                state = 'field_start'
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                handle_newline()
                pending = False
                state = 'field_start'
                i += 2
            else:
                field.append(c)
                i += 1
        elif state == 'quoted':
            if c == '"':
                state = 'quoted_end'
                i += 1
            else:
                field.append(c)
                i += 1
        elif state == 'quoted_end':
            if c == '"':
                # Escaped quote inside a quoted field
                field.append('"')
                state = 'quoted'
                i += 1
            elif c == ',':
                end_field()
                pending = True
                state = 'field_start'
                i += 1
            elif c == '\n':
                handle_newline()
                pending = False
                state = 'field_start'
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                handle_newline()
                pending = False
                state = 'field_start'
                i += 2
            else:
                raise ValueError(
                    f"Unexpected character {c!r} after closing quote at position {i}"
                )

    if state == 'quoted':
        raise ValueError("Unclosed quoted field")

    if pending:
        end_field()
        end_record()

    return records
