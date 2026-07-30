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
        if c == '"':
            # quoted field must start at beginning of field
            if current_field:
                raise ValueError("Characters before opening quote")
            i += 1
            # parse quoted content
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        current_field.append('"')
                        i += 2
                    else:
                        # closing quote
                        i += 1
                        # after closing quote: comma, newline, or EOF
                        if i < n:
                            nc = text[i]
                            if nc == ',':
                                end_field()
                                i += 1
                            elif nc == '\n':
                                end_record()
                                i += 1
                            elif nc == '\r':
                                if i + 1 < n and text[i + 1] == '\n':
                                    end_record()
                                    i += 2
                                else:
                                    end_record()
                                    i += 1
                            else:
                                raise ValueError("Characters after closing quote")
                        else:
                            end_record()
                        break
                else:
                    current_field.append(text[i])
                    i += 1
            else:
                # reached EOF without closing quote
                raise ValueError("Unclosed quote")
        elif c == ',':
            end_field()
            i += 1
        elif c == '\n':
            end_record()
            i += 1
        elif c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                end_record()
                i += 2
            else:
                end_record()
                i += 1
        else:
            current_field.append(c)
            i += 1

    # if we finished with data still in buffer (no trailing newline)
    if current_field or current_record:
        end_record()

    return records
