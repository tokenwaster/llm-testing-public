def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    in_quotes = False
    is_start_of_field = True
    i = 0
    n = len(text)
    last_char_was_newline = False

    while i < n:
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check for escaped double-quote (doubled quotes "")
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 1  # Skip the second quote
                else:
                    # End of quoted field
                    in_quotes = False
                    # Rule: Characters after a closing quote must be comma, newline, or EOF
                    next_idx = i + 1
                    if next_idx < n and text[next_idx] not in (',', '\n', '\r'):
                        raise ValueError("Malformed CSV: characters after closing quote")
            else:
                current_field.append(char)
        else:
            if char == '"' and is_start_of_field:
                # Field starts with a quote, so it's a quoted field
                in_quotes = True
            elif char == ',':
                # End of field
                current_record.append("".join(current_field))
                current_field = []
                is_start_of_field = True
            elif char == '\n' or char == '\r':
                # End of record
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                is_start_of_field = True
                last_char_was_newline = True
                # Handle \r\n by skipping the \n if it follows a \r
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                # Regular character in an unquoted field
                current_field.append(char)
                is_start_of_field = False

        i += 1

    # If the loop ends while still inside a quoted field, it's malformed
    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quote")

    # If the input did not end with a newline, we must finalize the last record and field.
    # A trailing newline at the end of the input does not create an extra record.
    if not last_char_was_newline:
        current_record.append("".join(current_field))
        records.append(current_record)

    return records
