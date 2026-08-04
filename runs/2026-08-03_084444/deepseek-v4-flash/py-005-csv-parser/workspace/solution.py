def parse_csv(text: str) -> list[list[str]]:
    rows = []
    record = []
    field = []
    in_quotes = False
    i = 0
    n = len(text)

    def finish_field():
        nonlocal record, field
        record.append(''.join(field))
        field = []

    def finish_record():
        nonlocal rows, record
        rows.append(record)
        record = []

    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped double quote
                    field.append('"')
                    i += 1  # skip the next double quote
                else:
                    # Closing double quote
                    in_quotes = False
                    # Check that the character after the closing quote,
                    # if any, is a valid delimiter
                    if i + 1 < n:
                        nxt = text[i + 1]
                        # Allowed: comma, newline (either \n or \r\n)
                        if nxt == ',' or nxt == '\n':
                            pass  # valid
                        elif nxt == '\r':
                            # Must be followed by \n to be a valid newline
                            if i + 2 >= n or text[i + 2] != '\n':
                                raise ValueError(
                                    "Invalid characters after closing quote"
                                )
                        else:
                            raise ValueError(
                                "Invalid characters after closing quote"
                            )
            else:
                field.append(c)
        else:  # not in quotes
            if c == '"':
                if len(field) == 0:
                    # Starting a quoted field
                    in_quotes = True
                else:
                    # Literal double quote inside an unquoted field
                    field.append(c)
            elif c == ',':
                finish_field()
            elif c == '\r':
                # Check for CRLF
                if i + 1 < n and text[i + 1] == '\n':
                    # Treat as a single newline
                    finish_field()
                    finish_record()
                    i += 1  # skip the '\n'
                else:
                    # Standalone '\r' is not a line terminator per spec
                    field.append(c)
            elif c == '\n':
                # Standalone '\n' or the '\n' from a CRLF already handled
                finish_field()
                finish_record()
            else:
                field.append(c)
        i += 1

    # End of input
    if in_quotes:
        raise ValueError("Unclosed quoted field")

    # Add the final record if there is any remaining data
    if field or record:
        record.append(''.join(field))
        rows.append(record)

    return rows
