def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i <= n:
        # Start of a new field
        if i == n:
            # End of input after a comma (trailing field) or we just finished a record
            # This case is handled by the record-finalization logic below
            current_record.append("")
            records.append(current_record)
            break

        ch = text[i]

        if ch == '"':
            # Quoted field
            i += 1
            field_chars = []
            while True:
                if i == n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    # Check if it's an escaped quote ""
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        break
                else:
                    field_chars.append(c)
                    i += 1
            # After closing quote, must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
            current_record.append("".join(field_chars))
        else:
            # Unquoted field - read until comma or newline
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))

        # Now i points to comma, newline, \r, or end of input
        if i == n:
            # End of input
            records.append(current_record)
            break
        elif text[i] == ',':
            i += 1
            # If next char is end of input, we have a trailing empty field
            if i == n:
                current_record.append("")
                records.append(current_record)
                break
        elif text[i] == '\r':
            # Handle \r\n
            i += 1
            if i < n and text[i] == '\n':
                i += 1
            # Check if this is the trailing newline at end of input
            if i == n:
                records.append(current_record)
                break
            records.append(current_record)
            current_record = []
        elif text[i] == '\n':
            i += 1
            # Check if this is the trailing newline at end of input
            if i == n:
                records.append(current_record)
                break
            records.append(current_record)
            current_record = []

    return records
