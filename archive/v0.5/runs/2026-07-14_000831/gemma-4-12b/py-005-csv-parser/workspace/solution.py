def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string into a list of records (lists of fields).
    Handles quoted fields, doubled double-quotes, and various newline formats.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if not in_quotes:
            if char == '"':
                # Quotes only have special meaning if the field starts with a quote.
                # A field "starts" if it's at the beginning of a record or after a comma.
                if current_field == "":
                    in_quotes = True
                else:
                    current_field += char
            elif char == ',':
                current_record.append(current_field)
                current_field = ""
            elif char == '\n':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            elif char == '\r':
                # Handle \r\n as a single record separator.
                if i + 1 < n and text[i+1] == '\n':
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    i += 1  # Skip the \n
                else:
                    # Treat lone \r as a literal character (RFC-4180 specifies \n or \r\n).
                    current_field += char
            else:
                current_field += char
        else:
            # Inside a quoted field.
            if char == '"':
                # Check for doubled double-quotes ("").
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 1
                else:
                    # Closing quote found.
                    in_quotes = False
                    # Rule: characters after a closing quote must be comma, newline, or EOF.
                    if i + 1 < n:
                        next_char = text[i+1]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Malformed input: character after closing quote")
            else:
                current_field += char
        i += 1

    # Error handling for unclosed quotes.
    if in_quotes:
        raise ValueError("Malformed input: unclosed quote")

    # Final record handling:
    # If the string doesn't end with a newline, we must add the final pending record/field.
    # A trailing newline at the end of the input does not create an extra record.
    if not text.endswith('\n') and not text.endswith('\r'):
        current_record.append(current_field)
        records.append(current_record)

    return records
