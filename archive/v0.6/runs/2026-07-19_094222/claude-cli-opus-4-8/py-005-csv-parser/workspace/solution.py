def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    field: list[str] = []
    record: list[str] = []
    i = 0
    n = len(text)

    # State flags for the current field.
    field_started = False   # any char consumed for this field
    quoted = False          # field began with a quote
    quote_closed = False    # closing quote seen for a quoted field

    def end_field():
        nonlocal field, field_started, quoted, quote_closed
        record.append("".join(field))
        field = []
        field_started = False
        quoted = False
        quote_closed = False

    def end_record():
        nonlocal record
        end_field()
        records.append(record)
        record = []

    while i < n:
        c = text[i]

        if quoted and not quote_closed:
            # Inside the quoted body.
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                    continue
                # Closing quote.
                quote_closed = True
                i += 1
                continue
            field.append(c)
            i += 1
            continue

        # Not inside an open quote.
        if c == ',':
            end_field()
            i += 1
            continue

        if c == '\n':
            end_record()
            i += 1
            continue

        if c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                end_record()
                i += 2
            else:
                end_record()
                i += 1
            continue

        if quote_closed:
            # After a closing quote, only comma/newline/EOF are allowed,
            # and those were handled above.
            raise ValueError("unexpected character after closing quote")

        if c == '"':
            if not field_started:
                # Field starts with a quote -> quoted field.
                field_started = True
                quoted = True
                i += 1
                continue
            # Quote in the middle of an unquoted field is literal.
            field.append(c)
            i += 1
            continue

        # Ordinary character.
        field_started = True
        field.append(c)
        i += 1

    # End of input.
    if quoted and not quote_closed:
        raise ValueError("unterminated quoted field")

    # Flush the final record (no trailing newline consumed it).
    end_record()

    return records
