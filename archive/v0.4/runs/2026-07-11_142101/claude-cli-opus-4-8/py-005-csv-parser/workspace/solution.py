def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    field: list[str] = []
    record: list[str] = []
    i = 0
    n = len(text)

    # State: are we at the start of a field (nothing consumed yet)?
    at_field_start = True
    have_data = False  # whether we've begun any record/field content

    def end_field():
        record.append("".join(field))
        field.clear()

    def end_record():
        end_field()
        records.append(record.copy())
        record.clear()

    while i < n:
        c = text[i]

        if at_field_start and c == '"':
            # Quoted field
            have_data = True
            i += 1
            while True:
                if i >= n:
                    raise ValueError("unterminated quoted field")
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field.append('"')
                        i += 2
                        continue
                    # closing quote
                    i += 1
                    break
                else:
                    field.append(ch)
                    i += 1
            # After closing quote, must be comma, newline, or EOF
            if i >= n:
                at_field_start = False
                # field ends at EOF
                break
            nxt = text[i]
            if nxt == ',':
                end_field()
                i += 1
                at_field_start = True
            elif nxt == '\n':
                end_record()
                i += 1
                at_field_start = True
                have_data = False
            elif nxt == '\r' and i + 1 < n and text[i + 1] == '\n':
                end_record()
                i += 2
                at_field_start = True
                have_data = False
            else:
                raise ValueError("invalid characters after closing quote")
            continue

        # Unquoted context
        if c == ',':
            have_data = True
            end_field()
            i += 1
            at_field_start = True
        elif c == '\n':
            have_data = True
            end_record()
            i += 1
            at_field_start = True
            have_data = False
        elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
            have_data = True
            end_record()
            i += 2
            at_field_start = True
            have_data = False
        else:
            have_data = True
            field.append(c)
            i += 1
            at_field_start = False

    # Flush the last field/record if there is pending content.
    # A trailing newline does not create an extra record: in that case
    # have_data is False and field/record are empty.
    if have_data or field or record:
        end_record()

    return records
