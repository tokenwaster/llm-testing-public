def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    field_chars: list[str] = []
    i = 0
    n = len(text)

    # State flags for the current field.
    in_quotes = False        # currently inside a quoted section
    field_started = False     # any char consumed for the current field
    was_quoted = False        # this field began with a quote (quotes are special)
    closed_quote = False      # a quoted section has been closed; only , \n \r or EOF may follow

    def end_field():
        nonlocal field_chars, field_started, was_quoted, closed_quote
        fields.append("".join(field_chars))
        field_chars = []
        field_started = False
        was_quoted = False
        closed_quote = False

    def end_record():
        nonlocal fields
        end_field()
        records.append(fields)
        fields = []

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                # Doubled quote -> literal quote, else close the quoted section.
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')
                    i += 2
                    continue
                in_quotes = False
                closed_quote = True
                i += 1
                continue
            else:
                field_chars.append(c)
                i += 1
                continue

        # Not inside quotes.
        if c == '"':
            if not field_started:
                # Field starts with a quote -> quoted field.
                in_quotes = True
                was_quoted = True
                field_started = True
                i += 1
                continue
            else:
                if was_quoted and closed_quote:
                    # Characters after a closing quote that aren't , \n \r EOF.
                    raise ValueError("unexpected character after closing quote")
                # Literal quote in an unquoted field (e.g. ab"cd).
                field_chars.append(c)
                i += 1
                continue

        if c == ',':
            end_field()
            i += 1
            continue

        if c == '\r':
            # Treat \r\n as a single record separator; a lone \r also separates.
            end_record()
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            continue

        if c == '\n':
            end_record()
            i += 1
            continue

        # Any other character.
        if was_quoted and closed_quote:
            raise ValueError("unexpected character after closing quote")
        field_chars.append(c)
        field_started = True
        i += 1

    if in_quotes:
        raise ValueError("unterminated quoted field")

    # Flush the final record unless the input ended exactly on a separator.
    if field_started or field_chars or fields:
        end_record()

    return records
