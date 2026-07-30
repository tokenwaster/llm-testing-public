def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    rows = []
    current_row = []
    current_field = ""
    in_quotes = False
    is_start_of_field = True
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check for escaped double-quote (doubled quotes "")
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 1  # Skip the second quote of the pair
                else:
                    # Closing quote encountered
                    in_quotes = False
                    # RFC-4180: Characters after a closing quote must be comma, newline, or EOF.
                    next_idx = i + 1
                    if next_idx < n:
                        next_char = text[next_idx]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Characters after closing quote")
            else:
                current_field += char
        else:
            if char == '"':
                if is_start_of_field:
                    in_quotes = True
                    is_start_of_field = False
                else:
                    # Rule: Quotes only have special meaning if the field starts with a quote.
                    current_field += '"'
            elif char == ',':
                current_row.append(current_field)
                current_field = ""
                is_start_of_field = True
            elif char == '\n' or (char == '\r' and i + 1 < n and text[i+1] == '\n'):
                # End of record
                current_row.append(current_field)
                rows.append(current_row)
                current_row = []
                current_field = ""
                is_start_of_field = True
                if char == '\r':
                    i += 1  # Skip the \n in \r\n
            else:
                current_field += char
                is_start_of_field = False

        i += 1

    # Handle end of input
    if in_quotes:
        raise ValueError("Unclosed quote")

    # If we ended while building a field (not at the start of a new one), add it.
    if not is_start_of_field:
        current_row.append(current_field)
        rows.append(current_row)
    # Special case: if the text ends with a comma, we must append an empty field.
    elif i > 0 and text[i-1] == ',':
        current_row.append("")
        rows.append(current_row)

    return rows
