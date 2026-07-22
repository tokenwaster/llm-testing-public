def parse_csv(text: str) -> list[list[str]]:
    """
    Parse RFC-4180-style CSV from scratch.
    Returns a list of records, each a list of field strings.
    Raises ValueError on malformed input.
    """
    records: list[list[str]] = []
    current_record: list[str] = []
    current_field_chars: list[str] = []
    in_quotes = False
    field_in_progress = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                # Could be escaped quote or closing quote
                if i + 1 < n and text[i + 1] == '"':
                    # Doubled quote -> single quote
                    current_field_chars.append('"')
                    i += 2
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
                    # After closing quote, only comma, newline, or EOF is allowed
                    if i < n:
                        next_c = text[i]
                        if next_c not in (',', '\n', '\r'):
                            raise ValueError(
                                "Unexpected character after closing quote"
                            )
            else:
                # Inside quotes, any character (including newlines/commas) is literal
                current_field_chars.append(c)
                i += 1
        else:  # not in quotes
            if c == '"':
                if not field_in_progress:
                    # Start of a quoted field
                    in_quotes = True
                    field_in_progress = True
                    i += 1
                else:
                    # Literal quote inside an unquoted field
                    current_field_chars.append('"')
                    i += 1
            elif c == ',':
                # Field separator: finish current field
                field = ''.join(current_field_chars)
                current_record.append(field)
                current_field_chars = []
                # A new (possibly empty) field starts after the comma
                field_in_progress = True
                i += 1
            elif c == '\n':
                # Record separator (LF)
                field = ''.join(current_field_chars)
                current_record.append(field)
                records.append(current_record)
                current_record = []
                current_field_chars = []
                field_in_progress = False
                i += 1
            elif c == '\r':
                # Record separator (CR or CRLF)
                field = ''.join(current_field_chars)
                current_record.append(field)
                records.append(current_record)
                current_record = []
                current_field_chars = []
                field_in_progress = False
                i += 1
                # Absorb optional LF
                if i < n and text[i] == '\n':
                    i += 1
            else:
                # Regular character inside an unquoted field
                if not field_in_progress:
                    field_in_progress = True
                current_field_chars.append(c)
                i += 1

    if in_quotes:
        raise ValueError("Unclosed quote")

    # Finalise the last record if necessary
    if field_in_progress:
        field = ''.join(current_field_chars)
        current_record.append(field)
        records.append(current_record)

    return records
