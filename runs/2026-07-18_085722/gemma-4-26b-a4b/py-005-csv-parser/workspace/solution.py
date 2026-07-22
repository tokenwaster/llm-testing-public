def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    rows = []
    current_row = []
    current_field = []
    state = "START"  # START, UNQUOTED, QUOTED, AFTER_QUOTE
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if state == "START":
            if char == '"':
                state = "QUOTED"
            elif char == ',':
                current_row.append("")
            elif char == '\n' or char == '\r':
                current_row.append("")
                rows.append(current_row)
                current_row = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                current_field.append(char)
                state = "UNQUOTED"

        elif state == "UNQUOTED":
            if char == ',':
                current_row.append("".join(current_field))
                current_field = []
                state = "START"
            elif char == '\n' or char == '\r':
                current_row.append("".join(current_field))
                current_field = []
                rows.append(current_row)
                current_row = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = "START"
            else:
                current_field.append(char)

        elif state == "QUOTED":
            if char == '"':
                state = "AFTER_QUOTE"
            else:
                current_field.append(char)

        elif state == "AFTER_QUOTE":
            if char == '"':
                # Escaped quote
                current_field.append('"')
                state = "QUOTED"
            elif char == ',':
                current_row.append("".join(current_field))
                current_field = []
                state = "START"
            elif char == '\n' or char == '\r':
                current_row.append("".join(current_field))
                current_field = []
                rows.append(current_row)
                current_row = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = "START"
            else:
                raise ValueError("Malformed CSV: characters after closing quote")

        i += 1

    # Final cleanup of the last field/row
    if state == "UNQUOTED":
        current_row.append("".join(current_field))
        rows.append(current_row)
    elif state == "QUOTED":
        raise ValueError("Malformed CSV: unclosed quote")
    elif state == "AFTER_QUOTE":
        current_row.append("".join(current_field))
        rows.append(current_row)
    elif state == "START":
        # If the string ended with a comma, we need to add an empty field.
        if current_row:
            current_row.append("")
            rows.append(current_row)

    return rows
