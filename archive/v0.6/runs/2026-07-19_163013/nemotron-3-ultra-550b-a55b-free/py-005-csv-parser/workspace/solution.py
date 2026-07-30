def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a CSV string according to RFC-4180 rules (from scratch).
    Returns a list of rows, each row being a list of field strings.
    Raises ValueError for malformed input (unclosed quote or stray characters after a closing quote).
    """
    rows: list[list[str]] = []
    current_row: list[str] = []
    current_field: list[str] = []
    i = 0
    n = len(text)
    # Possible states:
    # START_FIELD      - at the beginning of a field (after comma, newline, or start of input)
    # IN_UNQUOTED_FIELD - reading an unquoted field
    # IN_QUOTED_FIELD   - reading a quoted field
    # AFTER_QUOTE       - just closed a quoted field, expecting delimiter or EOF
    state = "START_FIELD"

    while i < n:
        ch = text[i]

        if state == "START_FIELD":
            if ch == '"':
                state = "IN_QUOTED_FIELD"
                i += 1
            elif ch == ',':
                current_row.append("")
                i += 1
            elif ch == "\n":
                current_row.append("")
                rows.append(current_row)
                current_row = []
                i += 1
            elif ch == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("")
                    rows.append(current_row)
                    current_row = []
                    i += 2
                else:
                    current_field.append(ch)
                    state = "IN_UNQUOTED_FIELD"
                    i += 1
            else:
                current_field.append(ch)
                state = "IN_UNQUOTED_FIELD"
                i += 1

        elif state == "IN_UNQUOTED_FIELD":
            if ch == ",":
                current_row.append("".join(current_field))
                current_field = []
                state = "START_FIELD"
                i += 1
            elif ch == "\n":
                current_row.append("".join(current_field))
                current_field = []
                rows.append(current_row)
                current_row = []
                state = "START_FIELD"
                i += 1
            elif ch == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("".join(current_field))
                    current_field = []
                    rows.append(current_row)
                    current_row = []
                    state = "START_FIELD"
                    i += 2
                else:
                    current_field.append(ch)
                    i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == "IN_QUOTED_FIELD":
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    state = "AFTER_QUOTE"
                    i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == "AFTER_QUOTE":
            if ch == ",":
                current_row.append("".join(current_field))
                current_field = []
                state = "START_FIELD"
                i += 1
            elif ch == "\n":
                current_row.append("".join(current_field))
                current_field = []
                rows.append(current_row)
                current_row = []
                state = "START_FIELD"
                i += 1
            elif ch == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    current_row.append("".join(current_field))
                    current_field = []
                    rows.append(current_row)
                    current_row = []
                    state = "START_FIELD"
                    i += 2
                else:
                    raise ValueError("Invalid character after closing quote")
            else:
                raise ValueError("Invalid character after closing quote")

    # End of input — finalize any pending field/row
    if state == "IN_QUOTED_FIELD":
        raise ValueError("Unclosed quoted field")
    elif state == "AFTER_QUOTE":
        current_row.append("".join(current_field))
        current_field = []
        rows.append(current_row)
        current_row = []
    elif state == "IN_UNQUOTED_FIELD":
        current_row.append("".join(current_field))
        current_field = []
        rows.append(current_row)
        current_row = []
    elif state == "START_FIELD":
        # Trailing comma (empty field) or empty input
        if current_row:
            current_row.append("")
            rows.append(current_row)
            current_row = []

    return rows
