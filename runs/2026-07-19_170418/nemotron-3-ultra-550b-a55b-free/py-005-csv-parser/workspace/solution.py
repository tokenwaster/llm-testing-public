def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a CSV string according to RFC-4180 rules (from scratch).
    Returns a list of records, each record being a list of fields.
    Raises ValueError on malformed input.
    """
    # Normalize line endings: treat \r\n as a single \n
    text = text.replace('\r\n', '\n')

    records: list[list[str]] = []
    current_record: list[str] = []
    current_field: list[str] = []  # characters of the current field
    i = 0
    n = len(text)

    # Parsing states
    # START_FIELD: beginning of a field (after comma, newline, or start of input)
    # IN_FIELD: reading an unquoted field
    # IN_QUOTED: reading a quoted field (after the opening quote)
    # AFTER_QUOTE: after the closing quote of a quoted field, expecting delimiter
    state = 'START_FIELD'

    while i < n:
        ch = text[i]

        if state == 'START_FIELD':
            if ch == '"':
                state = 'IN_QUOTED'
                i += 1
            elif ch == ',':
                # Empty field
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                # Empty field, end of record
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'START_FIELD'
                i += 1
            else:
                # Start of an unquoted field
                current_field.append(ch)
                state = 'IN_FIELD'
                i += 1

        elif state == 'IN_FIELD':
            if ch == ',':
                # End of field
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                # End of field and record
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'START_FIELD'
                i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 'IN_QUOTED':
            if ch == '"':
                # Check for escaped quote ("")
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 2
                else:
                    # Closing quote
                    state = 'AFTER_QUOTE'
                    i += 1
            elif ch == '\n':
                # Newline inside quoted field
                current_field.append('\n')
                i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 'AFTER_QUOTE':
            if ch == ',':
                # End of field
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                # End of field and record
                current_record.append(''.join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                state = 'START_FIELD'
                i += 1
            else:
                # Invalid character after closing quote
                raise ValueError("Invalid character after closing quote")

        else:
            # Should never happen
            raise RuntimeError("Invalid parser state")

    # End of input handling
    if state == 'IN_QUOTED':
        raise ValueError("Unclosed quoted field")
    elif state == 'AFTER_QUOTE':
        # Field ended with a closing quote, then EOF
        current_record.append(''.join(current_field))
        records.append(current_record)
    elif state == 'IN_FIELD' or state == 'START_FIELD':
        # If there is any pending content, finalize the last record
        if current_field or current_record:
            current_record.append(''.join(current_field))
            records.append(current_record)
    # Empty input results in empty list (records stays [])

    return records
