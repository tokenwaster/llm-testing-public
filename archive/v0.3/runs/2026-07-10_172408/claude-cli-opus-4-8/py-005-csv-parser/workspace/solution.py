def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    field: list[str] = []
    record: list[str] = []
    i = 0
    n = len(text)

    # State flags
    in_quotes = False
    field_started = False   # whether we've begun accumulating the current field
    quoted_field = False    # whether the current field started with a quote
    closed_quote = False    # whether a quoted field has seen its closing quote

    def end_field():
        nonlocal field, field_started, quoted_field, closed_quote
        record.append("".join(field))
        field = []
        field_started = False
        quoted_field = False
        closed_quote = False

    def end_record():
        nonlocal record
        end_field()
        records.append(record)
        record = []

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                # Could be an escaped quote or the closing quote
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                else:
                    in_quotes = False
                    closed_quote = True
                    i += 1
                    continue
            else:
                field.append(c)
                i += 1
                continue

        # Not in quotes
        if c == ',':
            end_field()
            i += 1
            continue

        if c == '\r':
            # Handle \r\n as a single record separator; lone \r also separates
            if i + 1 < n and text[i + 1] == '\n':
                end_record()
                i += 2
            else:
                end_record()
                i += 1
            continue

        if c == '\n':
            end_record()
            i += 1
            continue

        if c == '"':
            if not field_started:
                # Field starts with a quote -> quoted field
                field_started = True
                quoted_field = True
                in_quotes = True
                i += 1
                continue
            else:
                if closed_quote:
                    # Characters after a closing quote that aren't comma/newline/EOF
                    raise ValueError("unexpected quote after closing quote")
                # A quote in the middle of an unquoted field is literal
                field.append(c)
                i += 1
                continue

        # Any other character
        if quoted_field and closed_quote:
            # Non-comma/newline character after a closing quote -> malformed
            raise ValueError("unexpected character after closing quote")
        field_started = True
        field.append(c)
        i += 1

    if in_quotes:
        raise ValueError("unterminated quoted field")

    # Flush the final field/record if the input didn't end with a newline.
    # If it did end with a newline, record/field are already reset and empty.
    if record or field or field_started or quoted_field:
        end_record()

    return records
