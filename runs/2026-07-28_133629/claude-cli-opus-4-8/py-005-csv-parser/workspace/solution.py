def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    field_chars: list[str] = []
    i = 0
    n = len(text)
    # State: are we at the start of a field (nothing consumed yet)?
    at_field_start = True
    saw_any = False  # whether we've begun a record (to handle final trailing newline)

    def end_field():
        fields.append("".join(field_chars))
        field_chars.clear()

    def end_record():
        end_field()
        records.append(fields.copy())
        fields.clear()

    while i < n:
        saw_any = True
        if at_field_start and text[i] == '"':
            # Quoted field
            i += 1
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                c = text[i]
                if c == '"':
                    # Either an escaped quote or the closing quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                        continue
                    # Closing quote
                    i += 1
                    # Next char must be comma, newline, or EOF
                    if i >= n:
                        end_field()
                        at_field_start = True
                        break
                    nc = text[i]
                    if nc == ',':
                        end_field()
                        at_field_start = True
                        i += 1
                        break
                    elif nc == '\n':
                        end_record()
                        at_field_start = True
                        i += 1
                        break
                    elif nc == '\r' and i + 1 < n and text[i + 1] == '\n':
                        end_record()
                        at_field_start = True
                        i += 2
                        break
                    else:
                        raise ValueError("unexpected character after closing quote")
                else:
                    field_chars.append(c)
                    i += 1
        else:
            # Unquoted field
            c = text[i]
            if c == ',':
                end_field()
                at_field_start = True
                i += 1
            elif c == '\n':
                end_record()
                at_field_start = True
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                end_record()
                at_field_start = True
                i += 2
            else:
                field_chars.append(c)
                at_field_start = False
                i += 1

    # Handle the final field/record.
    # If the input ended exactly on a record separator, we've already closed
    # that record and should not emit an extra one (trailing newline rule).
    if not at_field_start:
        # We were in the middle of a field (unquoted, or nothing pending)
        end_record()
    else:
        # at_field_start is True: either input was empty of pending data,
        # or we just finished a field via comma/quote, or just closed a record.
        # We must emit a record if there is pending field data or pending fields,
        # or if the last consumed char was a field separator (comma) — but NOT
        # if the last char was a record separator.
        if field_chars or fields:
            end_record()
        elif saw_any and text[-1] == ',':
            end_record()

    return records
