def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    rows = []
    current_row = []
    current_field = []
    state = 'START_FIELD'  # START_FIELD, IN_UNQUOTED, IN_QUOTED, POST_QUOTE
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if state == 'START_FIELD':
            if char == '"':
                state = 'IN_QUOTED'
            elif char == ',':
                current_row.append("")
                current_field = []
            elif char in ('\r', '\n'):
                current_row.append("")
                rows.append(current_row)
                current_row = []
                current_field = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1  # Skip the \n part of \r\n
            else:
                state = 'IN_UNQUOTED'
                current_field = [char]

        elif state == 'IN_UNQUOTED':
            if char == ',':
                current_row.append("".join(current_field))
                current_field = []
                state = 'START_FIELD'
            elif char in ('\r', '\n'):
                current_row.append("".join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1  # Skip the \n part of \r\n
            else:
                current_field.append(char)

        elif state == 'IN_QUOTED':
            if char == '"':
                # Check for escaped quote ""
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 1  # Skip the second quote
                else:
                    state = 'POST_QUOTE'
            else:
                current_field.append(char)

        elif state == 'POST_QUOTE':
            if char == ',':
                current_row.append("".join(current_field))
                current_field = []
                state = 'START_FIELD'
            elif char in ('\r', '\n'):
                current_row.append("".join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1  # Skip the \n part of \n\r
            else:
                raise ValueError("Characters after closing quote")

        i += 1

    # Finalize the last field/row if we didn't end on a newline or comma
    if state == 'IN_UNQUOTED':
        current_row.append("".join(current_field))
        rows.append(current_row)
    elif state == 'IN_QUOTED':
        raise ValueError("Unclosed quote")
    elif state == 'POST_QUOTE':
        current_row.append("".join(current_field))
        rows.append(current_row)
    elif state == 'START_FIELD':
        # If the loop ended because of a trailing comma, add an empty field
        if n > 0 and text[n-1] == ',':
            current_row.append("")
            rows.append(current_row)

    return rows
