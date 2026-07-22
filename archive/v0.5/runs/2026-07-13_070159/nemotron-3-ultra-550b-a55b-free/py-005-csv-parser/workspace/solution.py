def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a CSV string according to RFC 4180 rules (from scratch).

    - Fields are separated by commas; records by \\n or \\r\\n.
    - A field wrapped in double quotes may contain commas, newlines, and doubled double-quotes (\"\" -> \").
    - Quotes only have special meaning if the field starts with a quote.
    - Empty fields decode to empty strings.
    - Trailing newline does not create an extra record; an empty line in the middle is a record with one empty field.
    - parse_csv(\"\") returns [].
    - Malformed input (unclosed quote, or characters after a closing quote that aren't comma/newline/EOF) raises ValueError.
    """
    if text == "":
        return []

    n = len(text)
    i = 0
    result: list[list[str]] = []
    current_record: list[str] = []
    current_field: list[str] = []
    # state: 0 = start of field, 1 = in unquoted field, 2 = in quoted field, 3 = after closing quote
    state = 0

    while i < n:
        ch = text[i]
        if state == 0:  # start of field
            if ch == '"':
                state = 2
                i += 1
            elif ch == ',':
                # empty field
                current_record.append(''.join(current_field))
                current_field = []
                i += 1
            else:
                # check for newline (record separator)
                newline_len = 0
                if ch == '\n':
                    newline_len = 1
                elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    newline_len = 2
                if newline_len:
                    # end of record
                    current_record.append(''.join(current_field))
                    current_field = []
                    result.append(current_record)
                    current_record = []
                    i += newline_len
                else:
                    # start unquoted field
                    current_field.append(ch)
                    state = 1
                    i += 1

        elif state == 1:  # in unquoted field
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 0
                i += 1
            else:
                newline_len = 0
                if ch == '\n':
                    newline_len = 1
                elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    newline_len = 2
                if newline_len:
                    current_record.append(''.join(current_field))
                    current_field = []
                    result.append(current_record)
                    current_record = []
                    state = 0
                    i += newline_len
                else:
                    current_field.append(ch)
                    i += 1

        elif state == 2:  # in quoted field
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # escaped quote
                    current_field.append('"')
                    i += 2
                else:
                    # closing quote
                    state = 3
                    i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 3:  # after closing quote
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 0
                i += 1
            else:
                newline_len = 0
                if ch == '\n':
                    newline_len = 1
                elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    newline_len = 2
                if newline_len:
                    current_record.append(''.join(current_field))
                    current_field = []
                    result.append(current_record)
                    current_record = []
                    state = 0
                    i += newline_len
                else:
                    raise ValueError("Malformed CSV: unexpected character after closing quote")

    # End of input handling
    if state == 1:
        current_record.append(''.join(current_field))
    elif state == 2:
        raise ValueError("Unclosed quoted field")
    elif state == 3:
        current_record.append(''.join(current_field))
    elif state == 0 and current_record:
        # trailing comma: there is a pending empty field
        current_record.append(''.join(current_field))  # current_field is empty

    if current_record:
        result.append(current_record)

    return result
