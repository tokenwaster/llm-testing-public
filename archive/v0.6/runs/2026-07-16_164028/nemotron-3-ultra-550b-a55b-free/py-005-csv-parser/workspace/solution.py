def parse_csv(text: str) -> list[list[str]]:
    """
    Parse an RFC-4180 style CSV string without using the csv module.

    Args:
        text: The CSV input as a string.

    Returns:
        A list of records, each record being a list of field strings.

    Raises:
        ValueError: If the input is malformed (unclosed quote, stray characters after a closing quote, etc.).
    """
    records = []
    current_record = []
    current_field = []  # list of characters for the field being built
    state = 'START_FIELD'  # possible states: START_FIELD, IN_UNQUOTED, IN_QUOTED, AFTER_QUOTE
    i = 0
    n = len(text)

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
                i += 1
            elif ch == '\n':
                # End of record (empty field)
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    # CRLF line ending
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    i += 2
                else:
                    # Lone CR is treated as data
                    current_field.append(ch)
                    state = 'IN_UNQUOTED'
                    i += 1
            else:
                # Start of an unquoted field
                current_field.append(ch)
                state = 'IN_UNQUOTED'
                i += 1

        elif state == 'IN_UNQUOTED':
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'START_FIELD'
                    i += 2
                else:
                    current_field.append(ch)
                    i += 1
            else:
                current_field.append(ch)
                i += 1

        elif state == 'IN_QUOTED':
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped quote ("" -> ")
                    current_field.append('"')
                    i += 2
                else:
                    # Closing quote
                    state = 'AFTER_QUOTE'
                    i += 1
            else:
                # Any other character (including commas, newlines) is literal
                current_field.append(ch)
                i += 1

        elif state == 'AFTER_QUOTE':
            if ch == ',':
                current_record.append(''.join(current_field))
                current_field = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\n':
                current_record.append(''.join(current_field))
                current_field = []
                records.append(current_record)
                current_record = []
                state = 'START_FIELD'
                i += 1
            elif ch == '\r':
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    current_field = []
                    records.append(current_record)
                    current_record = []
                    state = 'START_FIELD'
                    i += 2
                else:
                    raise ValueError("Malformed CSV: unexpected character after closing quote")
            else:
                raise ValueError("Malformed CSV: unexpected character after closing quote")

        else:
            # Should never happen
            raise ValueError("Invalid parser state")

    # End-of-input handling
    if state == 'IN_UNQUOTED':
        current_record.append(''.join(current_field))
        if current_record:
            records.append(current_record)
    elif state == 'IN_QUOTED':
        raise ValueError("Malformed CSV: unclosed quoted field")
    elif state == 'AFTER_QUOTE':
        current_record.append(''.join(current_field))
        if current_record:
            records.append(current_record)
    elif state == 'START_FIELD':
        if current_record:
            # Trailing comma -> final empty field
            current_record.append(''.join(current_field))  # current_field is empty
            records.append(current_record)
        # else: trailing newline or empty input -> nothing to add

    return records
