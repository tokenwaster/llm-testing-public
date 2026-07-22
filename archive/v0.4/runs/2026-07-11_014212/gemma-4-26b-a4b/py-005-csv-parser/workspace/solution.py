def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    # States: START (beginning of field), UNQUOTED, QUOTED, POST_QUOTE (after a quote in a quoted field)
    state = 'START'
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if state == 'START':
            if char == '"':
                state = 'QUOTED'
            elif char == ',':
                current_record.append("")
                current_field = []
            elif char in '\r\n':
                # A newline at the start of a field (or after a comma) ends the current record
                # with an empty field, unless it is the very last character of the file.
                is_last = (i + 1 >= n) or (char == '\r' and i + 2 >= n)
                if not is_last:
                    current_record.append("")
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    if char == '\r' and i + 1 < n and text[i+1] == '\n':
                        i += 1
                    state = 'START'
                else:
                    # If it is the last character, we don't start a new record.
                    # However, if the input was just "\n", we must ensure we return [[""]].
                    if not records and not current_record:
                        records.append([""])
                    state = 'START'
            else:
                state = 'UNQUOTED'
                current_field.append(char)

        elif state == 'UNQUOTED':
            if char == ',':
                current_record.append("".join(current_field))
                current_field = []
                state = 'START'
            elif char in '\r\n':
                # A newline ends the current field and the current record.
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = 'START'
            else:
                current_field.append(char)

        elif state == 'QUOTED':
            if char == '"':
                state = 'POST_QUOTE'
            else:
                current_field.append(char)

        elif state == 'POST_QUOTE':
            if char == '"':
                # Escaped quote: "" -> "
                current_field.append('"')
                state = 'QUOTED'
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                state = 'START'
            elif char in '\r\n':
                # A newline ends the current field and the current record.
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = 'START'
            else:
                # Characters after a closing quote that aren't delimiters are malformed.
                raise ValueError("Malformed CSV: characters found after closing quote")

        i += 1

    # Final cleanup for the last field/record in the file
    if state == 'QUOTED':
        raise ValueError("Malformed CSV: unclosed quoted field")

    if state == 'UNQUOTED' or state == 'POST_QUOTE':
        current_record.append("".join(current_field))
        records.append(current_record)
    elif state == 'START':
        # If the loop ended while in START, it means the last character was a comma or newline.
        # If it was a comma, we must add an empty field to the current record.
        if i > 0 and text[i-1] == ',':
            current_record.append("")
            records.append(current_record)

    return records
