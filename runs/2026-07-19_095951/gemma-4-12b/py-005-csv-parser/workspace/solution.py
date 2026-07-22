def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string into a list of records (lists of strings).
    Handles quoted fields, escaped quotes, and various newline formats.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    in_quotes = False
    at_field_start = True
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check for doubled double-quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote
                    in_quotes = False
                    next_idx = i + 1
                    # Rule: characters after a closing quote must be comma, newline, or EOF
                    if next_idx < n:
                        next_char = text[next_idx]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Malformed input")
            else:
                current_field.append(char)
            i += 1
        else:
            if char == '"':
                # Quotes only have special meaning if they start a field
                if at_field_start:
                    in_quotes = True
                    i += 1
                else:
                    current_field.append('"')
                    i += 1
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                at_field_start = True
                i += 1
            elif char == '\n':
                # A newline at the very end of the input does not create an extra record
                if i != n - 1:
                    current_record.append("".join(current_field))
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    at_field_start = True
                i += 1
            elif char == '\r':
                # Handle \r\n as a single newline unit
                if i + 1 < n and text[i+1] == '\n':
                    if i + 2 != n: # Not at the very end of the input
                        current_record.append("".join(current_field))
                        records.append(current_record)
                        current_record = []
                        current_field = []
                        at_field_start = True
                    i += 2
                else:
                    # Handle \r as a newline (legacy Mac style)
                    if i != n - 1:
                        current_record.append("".join(current_field))
                        records.append(current_record)
                        current_record = []
                        current_field = []
                        at_field_start = True
                    i += 1
            else:
                current_field.append(char)
                at_field_start = False
                i += 1

    if in_quotes:
        raise ValueError("Malformed input")

    # Add the final record if there is any content remaining
    if current_record or current_field:
        records.append(current_record + ["".join(current_field)])

    return records
