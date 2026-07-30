def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string according to RFC-4180 rules from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    in_quotes = False
    start_of_field = True
    last_char_was_newline = False
    i = 0

    while i < len(text):
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check for escaped double-quote ("")
                if i + 1 < len(text) and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    in_quotes = False
                    i += 1
                    # Malformed input: characters after closing quote must be comma, newline, or EOF
                    if i < len(text) and text[i] not in (',', '\n', '\r'):
                        raise ValueError("Malformed CSV: unexpected character after closing quote")
            else:
                current_field.append(char)
                i += 1
        else:
            # Not currently inside a quoted field
            if start_of_field and char == '"':
                in_quotes = True
                start_of_field = False
                i += 1
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                start_of_field = True
                i += 1
            elif char == '\n':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                start_of_field = True
                last_char_was_newline = True
                i += 1
            elif char == '\r':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                start_of_field = True
                last_char_was_newline = True
                # Handle CRLF (\r\n)
                if i + 1 < len(text) and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                current_field.append(char)
                start_of_field = False
                i += 1

    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quote")

    # If the input did not end with a newline, we must process the final pending record.
    # A trailing newline at the end of the input does not create an extra record.
    if not last_char_was_newline:
        current_record.append("".join(current_field))
        records.append(current_record)

    return records
