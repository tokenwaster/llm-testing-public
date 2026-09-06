def parse_csv(text: str) -> list[list[str]]:
    """Parse an RFC-4180-style CSV string from scratch."""
    
    if not text:
        return []

    rows = []
    current_row = []
    current_field_chars = []
    in_quoted = False

    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        # Handle record separator: \r\n
        if char == '\r' and i + 1 < n and text[i + 1] == '\n':
            # End of record
            if in_quoted:
                raise ValueError("Unclosed quoted field")
            current_field_chars.append(char)
            current_row.append("".join(current_field_chars))
            rows.append(current_row)
            current_field_chars = []
            current_row = []
            i += 2
            continue

        # Handle record separator: \n
        if char == '\n':
            if in_quoted:
                raise ValueError("Unclosed quoted field")
            current_row.append("".join(current_field_chars))
            rows.append(current_row)
            current_field_chars = []
            current_row = []
            i += 1
            continue

        # Field content
        if not in_quoted:
            if char == '"':
                # Start quoted field
                in_quoted = True
            else:
                current_field_chars.append(char)
        else:
            # Inside quoted field
            if char == '"':
                # Check for escaped quote "" or ending quote
                if i + 1 < n and text[i + 1] == '"':
                    current_field_chars.append('"')
                    i += 1
                else:
                    # End of quoted field
                    in_quoted = False
            else:
                current_field_chars.append(char)

        i += 1

    # Finish last field and row
    if in_quoted:
        raise ValueError("Unclosed quoted field")

    # Check for invalid trailing characters after closing quote
    if current_field_chars or current_row:
        # If last char was a quote ending a field, next non-whitespace shouldn't exist
        # (Handled in loop by raising error on extra chars, but check final state)
        rows.append(current_row)
        return rows
    
    # If we had rows but no field chars left (trailing newline), do nothing
    if rows:
        return rows
    return []
