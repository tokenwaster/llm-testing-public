def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string according to RFC-4180 rules from scratch.
    """
    if not text:
        return []

    rows = []
    current_row = []
    i = 0
    n = len(text)
    last_char_was_newline = False

    while i < n:
        # Reset newline flag at the start of each field processing attempt
        last_char_was_newline = False
        field_chars = []
        
        if text[i] == '"':
            # --- Quoted Field Logic ---
            i += 1  # Skip opening quote
            while True:
                if i >= n:
                    raise ValueError("Unclosed quote")
                if text[i] == '"':
                    # Check for escaped double-quote ("")
                    if i + 1 < n and text[i+1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote found
                        i += 1
                        break
                else:
                    field_chars.append(text[i])
                    i += 1

            field_val = "".join(field_chars)
            if i < n:
                char = text[i]
                if char == ',':
                    current_row.append(field_val)
                    i += 1
                elif char == '\r':
                    current_row.append(field_val)
                    rows.append(current_row)
                    current_row = []
                    # Handle CRLF or just CR
                    if i + 1 < n and text[i+1] == '\n':
                        i += 2
                    else:
                        i += 1
                    last_char_was_newline = True
                elif char == '\n':
                    current_row.append(field_val)
                    rows.append(current_row)
                    current_row = []
                    i += 1
                    last_char_was_newline = True
                else:
                    # RFC-4180: characters after closing quote must be comma, newline or EOF
                    raise ValueError("Invalid character after closing quote")
            else:
                # End of input reached immediately after closing quote
                current_row.append(field_val)
                i += 1
        else:
            # --- Unquoted Field Logic ---
            start = i
            while i < n and text[i] != ',' and text[i] != '\n' and text[i] != '\r':
                i += 1
            field_val = text[start:i]
            current_row.append(field_val)

            if i < n:
                char = text[i]
                if char == ',':
                    i += 1
                elif char == '\r':
                    rows.append(current_row)
                    current_row = []
                    # Handle CRLF or just CR
                    if i + 1 < n and text[i+1] == '\n':
                        i += 2
                    else:
                        i += 1
                    last_char_was_newline = True
                elif char == '\n':
                    rows.append(current_row)
                    current_row = []
                    i += 1
                    last_char_was_newline = True
            else:
                # End of input reached
                i += 1

    # A trailing newline does not create an extra record, but if the text didn't end with one,
    # we must add the final accumulated row.
    if not last_char_was_newline and n > 0:
        rows.append(current_row)

    return rows
