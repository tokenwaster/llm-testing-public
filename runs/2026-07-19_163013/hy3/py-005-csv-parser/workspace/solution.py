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

        if c == "\n" or c == "\r":
            # handle line ending
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
                raise ValueError("characters before opening quote")
            i += 1
            # parse quoted content
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        current_field.append('"')
                        i += 2
                        continue
                    else:
                        # closing quote
                        i += 1
                        # after closing quote: comma, newline, or EOF
                        if i < n:
                            nxt = text[i]
                            if nxt == ",":
                                end_field()
                                i += 1
                                break
                            elif nxt == "\n":
                                end_record()
                                i += 1
                                break
                            elif nxt == "\r":
                                if i + 1 < n and text[i + 1] == "\n":
                                    end_record()
                                    i += 2
                                    break
                                else:
                                    end_record()
                                    i += 1
                                    break
                            else:
                                raise ValueError("characters after closing quote")
                        else:
                            end_field()
                            break
                else:
                    current_field.append(ch)
                    i += 1
            else:
                # reached EOF without closing quote
                raise ValueError("unterminated quote")
            continue

        # normal unquoted character
        current_field.append(c)
        i += 1

    # if we finished with data still in buffer (no trailing newline)
    if current_field or current_record:
        end_record()

    return records
