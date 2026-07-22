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
            # End of input after a record separator or at start
            current_record.append("")
            records.append(current_record)
            break

        if text[i] == '"':
            # Quoted field
            i += 1  # skip opening quote
            field_chars = []
            closed = False
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        i += 1  # skip closing quote
                        closed = True
                        break
                else:
                    field_chars.append(ch)
                    i += 1
            if not closed:
                raise ValueError("Unclosed quoted field")
            # After closing quote, must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
            current_record.append("".join(field_chars))
        else:
            # Unquoted field: read until comma or newline
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))

        # Now i points at comma, newline, \r, or end of input
        if i == n:
            records.append(current_record)
            break
        elif text[i] == ',':
            i += 1  # move past comma, continue to next field
        elif text[i] == '\r':
            i += 1
            if i < n and text[i] == '\n':
                i += 1
            records.append(current_record)
            current_record = []
            # If this was the last character(s), don't add empty record
            if i == n:
                break
        elif text[i] == '\n':
            i += 1
            records.append(current_record)
            current_record = []
            # If this was the last character, don't add empty record
            if i == n:
                break

    return records
