def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string according to RFC-4180 rules from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)
    last_char_was_comma = False

    while i < n:
        # --- 1. Parse Field ---
        if text[i] == '"':
            # Quoted field logic
            i += 1  # Skip opening quote
            field_chars = []
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
            
            current_record.append("".join(field_chars))

            # RFC-4180: Characters after a closing quote must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError("Characters after closing quote")
        else:
            # Unquoted field logic
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))

        # --- 2. Handle Separator ---
        if i < n:
            if text[i] == ',':
                i += 1
                last_char_was_comma = True
            elif text[i] == '\r':
                # Handle \r\n or just \r as record separators
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                records.append(current_record)
                current_record = []
                last_char_was_comma = False
            elif text[i] == '\n':
                # Handle \n as record separator
                i += 1
                records.append(current_record)
                current_record = []
                last_char_was_comma = False

    # If the input ends with a comma, there is an implicit empty field at the end of the last record
    if last_char_was_comma:
        current_record.append("")

    # Add the final record if it exists (handles cases where text doesn't end in newline)
    if current_record:
        records.append(current_record)

    return records
