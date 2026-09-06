def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    current_row: list[str] = []
    field: list[str] = []

    # states: START, UNQUOTED, QUOTED, AFTER_QUOTE
    state = "START"

    n = len(text)
    i = 0

    while i < n:
        c = text[i]

        if state == "START":
            if c == '"':
                state = "QUOTED"
                i += 1
            elif c == ",":
                current_row.append("".join(field))
                field = []
                # stay in START
                i += 1
            elif c == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("".join(field))
                    field = []
                    rows.append(current_row)
                    current_row = []
                    state = "START"
                    i += 2
                else:
                    # lone \r is data
                    field.append(c)
                    state = "UNQUOTED"
                    i += 1
            elif c == "\n":
                current_row.append("".join(field))
                field = []
                rows.append(current_row)
                current_row = []
                state = "START"
                i += 1
            else:
                field.append(c)
                state = "UNQUOTED"
                i += 1

        elif state == "UNQUOTED":
            if c == ",":
                current_row.append("".join(field))
                field = []
                state = "START"
                i += 1
            elif c == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("".join(field))
                    field = []
                    rows.append(current_row)
                    current_row = []
                    state = "START"
                    i += 2
                else:
                    field.append(c)
                    i += 1
            elif c == "\n":
                current_row.append("".join(field))
                field = []
                rows.append(current_row)
                current_row = []
                state = "START"
                i += 1
            else:
                # '"' here is literal
                field.append(c)
                i += 1

        elif state == "QUOTED":
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    state = "AFTER_QUOTE"
                    i += 1
            elif c == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    field.append("\r")
                    field.append("\n")
                    i += 2
                else:
                    field.append(c)
                    i += 1
            else:
                field.append(c)
                i += 1

        elif state == "AFTER_QUOTE":
            if c == ",":
                current_row.append("".join(field))
                field = []
                state = "START"
                i += 1
            elif c == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("".join(field))
                    field = []
                    rows.append(current_row)
                    current_row = []
                    state = "START"
                    i += 2
                else:
                    raise ValueError("malformed CSV: characters after closing quote")
            elif c == "\n":
                current_row.append("".join(field))
                field = []
                rows.append(current_row)
                current_row = []
                state = "START"
                i += 1
            else:
                raise ValueError("malformed CSV: characters after closing quote")
        else:
            raise AssertionError("unknown state")

    # EOF handling
    if state == "START":
        if len(current_row) == 0 and len(field) == 0:
            # empty input (already handled) or just after a newline: no extra record
            pass
        else:
            # trailing comma case: pending empty field
            current_row.append("".join(field))
            rows.append(current_row)
    elif state == "UNQUOTED":
        current_row.append("".join(field))
        rows.append(current_row)
    elif state == "QUOTED":
        raise ValueError("malformed CSV: unclosed quote")
    elif state == "AFTER_QUOTE":
        current_row.append("".join(field))
        rows.append(current_row)

    return rows
