def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch without using the csv module.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    in_quotes = False
    start_of_field = True

    while i < n:
        char = text[i]

        if not in_quotes:
            # A field is quoted only if it starts with a double quote
            if start_of_field and char == '"':
                in_quotes = True
                start_of_field = False
                i += 1
            elif char == ',':
                # End of field
                current_record.append("".join(current_field))
                current_field = []
                start_of_field = True
                i += 1
            elif char == '\n':
                # End of record (Unix style)
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                start_of_field = True
                i += 1
            elif char == '\r':
                # End of record (Windows style \r\n or old Mac \r)
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                start_of_field = True
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                # Literal character in non-quoted field
                current_field.append(char)
                start_of_field = False
                i += 1
        else:  # inside a quoted field
            if char == '"':
                # Check for escaped double quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # Closing quote encountered
                    in_quotes = False
                    i += 1
                    # RFC-4180: characters after closing quote must be comma, newline, or EOF
                    if i < n:
                        next_char = text[i]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError("Malformed CSV: unexpected character after closing quote")
            else:
                # Literal character inside quotes (including commas and newlines)
                current_field.append(char)
                i += 1

    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quoted field")

    # Handle the final record if the input didn't end with a newline sequence
    if n > 0 and text[-1] not in ('\n', '\r'):
        current_record.append("".join(current_field))
        records.append(current_record)

    return records
