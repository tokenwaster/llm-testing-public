def parse_csv(text: str) -> list[list[str]]:
    records = []
    if text == "":
        return records

    i = 0
    n = len(text)
    current_record = []
    current_field = []

    def end_field():
        nonlocal current_field
        current_record.append("".join(current_field))
        current_field = []

    def end_record():
        nonlocal current_record
        end_field()
        records.append(current_record)
        current_record = []

    while i < n:
        c = text[i]

        if c == "\r" or c == "\n":
            # end of record
            if c == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    i += 2
                else:
                    i += 1
            else:
                i += 1
            end_record()
            continue

        if c == ",":
            end_field()
            i += 1
            continue

        if c == '"':
            # quoted field must start at beginning of field
            if current_field:
                raise ValueError("Unexpected quote in middle of unquoted field")
            i += 1
            # parse quoted content
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        current_field.append('"')
                        i += 2
                    else:
                        # closing quote
                        i += 1
                        # after closing quote: comma, newline, or EOF
                        if i < n and text[i] not in (",", "\r", "\n"):
                            raise ValueError("Characters after closing quote")
                        break
                else:
                    current_field.append(ch)
                    i += 1
            else:
                # reached EOF without closing quote
                raise ValueError("Unclosed quote")
            # do not consume the comma/newline here; loop will handle
            continue

        # normal character in unquoted field
        current_field.append(c)
        i += 1

    # handle last field/record if not ended by newline
    if current_field or current_record:
        end_record()

    return records
