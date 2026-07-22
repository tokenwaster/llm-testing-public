def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    rows = []
    current_row = []
    current_field = []
    in_quotes = False
    i = 0
    n = len(text)
    last_char_was_newline = False

    while i < n:
        char = text[i]

        if not in_quotes:
            if char == '"':
                # A field starts with a quote only if it's the beginning of the field.
                if not current_field:
                    in_quotes = True
                else:
                    # If we are already in an unquoted field, quotes are literal.
                    current_field.append(char)
            elif char == ',':
                # End of a field.
                current_row.append("".join(current_field))
                current_field = []
            elif char == '\n' or char == '\r':
                # End of a record.
                current_row.append("".join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                last_char_was_newline = True
                # Handle \r\n by skipping the \n if we just processed \r.
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                current_field.append(char)
        else:
            # Inside a quoted field.
            if char == '"':
                # Check for escaped double-quotes ("").
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 1  # Skip the second quote.
                else:
                    # Closing quote encountered.
                    in_quotes = False
                    # RFC-4180: Characters after a closing quote must be comma, newline, or EOF.
                    if i + 1 < n and text[i+1] not in (',', '\n', '\r'):
                        raise ValueError("Malformed CSV: characters after closing quote")
            else:
                # Inside quotes, everything is literal including commas and newlines.
                current_field.append(char)

        i += 1

    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quote")

    # If the input did not end with a newline, we must finalize the last field and row.
    if not last_char_was_newline:
        current_row.append("".join(current_field))
        rows.append(current_row)

    return rows
