def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = ""
    state = "START"  # START, UNQUOTED, QUOTED, POST_QUOTE
    i = 0
    n = len(text)
    last_char_was_comma = False
    has_active_record = False

    while i < n:
        char = text[i]

        if state == "START":
            has_active_record = True
            if char == '"':
                state = "QUOTED"
            elif char == ',':
                current_record.append("")
                last_char_was_comma = True
            elif char == '\n' or char == '\r':
                current_record.append("")
                records.append(current_record)
                current_record = []
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                last_char_was_comma = False
            else:
                state = "UNQUOTED"
                current_field = char
        
        elif state == "UNQUOTED":
            if char == ',':
                current_record.append(current_field)
                current_field = ""
                state = "START"
                last_char_was_comma = True
            elif char == '\n' or char == '\r':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = "START"
                last_char_was_comma = False
            else:
                current_field += char
        
        elif state == "QUOTED":
            if char == '"':
                # Check for doubled double-quotes (escaped quote)
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 1  # Skip the second quote
                else:
                    state = "POST_QUOTE"
            else:
                current_field += char
        
        elif state == "POST_QUOTE":
            if char == ',':
                current_record.append(current_field)
                current_field = ""
                state = "START"
                last_char_was_comma = True
            elif char == '\n' or char == '\r':
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                state = "START"
                last_char_was_comma = False
            else:
                raise ValueError("Characters after closing quote")

        i += 1

    # Finalize the parsing process for any remaining data
    if state == "UNQUOTED":
        current_record.append(current_field)
        records.append(current_record)
    elif state == "QUOTED":
        raise ValueError("Unclosed quote")
    elif state == "POST_QUOTE":
        current_record.append(current_field)
        records.append(current_record)
    elif state == "START" and has_active_record:
        if last_char_was_comma:
            current_record.append("")
            records.append(current_record)

    return records
