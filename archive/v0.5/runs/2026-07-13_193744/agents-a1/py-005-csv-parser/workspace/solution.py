def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180 rules without using the csv module."""
    result = []
    current_record = []
    current_field = []
    state = "NORMAL"  # NORMAL or IN_QUOTE
    expecting_separator = False  # True after a closing quote, before next separator
    i = 0
    n = len(text)

    while i < n:
        if state == "NORMAL":
            if expecting_separator:
                ch = text[i]
                if ch == ',':
                    # End current field and start new one
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
                    expecting_separator = False
                elif ch == '\n':
                    # Record end (LF)
                    current_record.append(''.join(current_field))
                    result.append(current_record)
                    current_record = []
                    current_field = []
                    i += 1
                    expecting_separator = False
                elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    # Record end (CRLF)
                    current_record.append(''.join(current_field))
                    result.append(current_record)
                    current_record = []
                    current_field = []
                    i += 2
                    expecting_separator = False
                else:
                    raise ValueError(f"Invalid character after quote: {ch!r}")
            else:
                ch = text[i]
                if ch == ',':
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
                elif ch == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        # CRLF record separator
                        current_record.append(''.join(current_field))
                        result.append(current_record)
                        current_record = []
                        current_field = []
                        i += 2
                    else:
                        # Lone CR is part of the field
                        current_field.append(ch)
                        i += 1
                elif ch == '\n':
                    # LF record separator
                    current_record.append(''.join(current_field))
                    result.append(current_record)
                    current_record = []
                    current_field = []
                    i += 1
                elif ch == '"':
                    # Start quoted field only if this is the first character of the field
                    if not current_field:
                        state = "IN_QUOTE"
                        i += 1
                    else:
                        current_field.append(ch)
                        i += 1
                else:
                    current_field.append(ch)
                    i += 1
        elif state == "IN_QUOTE":
            if text[i] == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped quote
                    current_field.append('"')
                    i += 2
                else:
                    # End of quoted field
                    state = "NORMAL"
                    expecting_separator = True
                    i += 1
            elif text[i] == '\r':
                # Carriage return inside quoted field is part of the content
                current_field.append(text[i])
                i += 1
            elif text[i] == '\n':
                # Newline inside quoted field is part of the content
                current_field.append(text[i])
                i += 1
            else:
                current_field.append(text[i])
                i += 1

    # After processing all characters, handle final state
    if state == "IN_QUOTE":
        raise ValueError("Unclosed quote")

    if state == "NORMAL":
        if expecting_separator:
            # EOF immediately after a closing quote; finalize the record
            current_record.append(''.join(current_field))
            result.append(current_record)
        else:
            # There may be an unfinished field or record
            if current_field or current_record:
                current_record.append(''.join(current_field))
                result.append(current_record)

    return result
