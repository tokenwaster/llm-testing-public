def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i <= n:
        # Check if we're at end of input
        if i == n:
            current_record.append("")
            records.append(current_record)
            break

        # Check for record separator (empty line in middle = one record with one empty field)
        if text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 2
            # If this was a trailing newline, stop
            if i == n:
                break
        elif text[i] == '\n':
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 1
            # If this was a trailing newline, stop
            if i == n:
                break
        elif text[i] == ',':
            current_record.append("")
            i += 1
        elif text[i] == '"':
            # Quoted field
            i += 1
            field_chars = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        # Escaped quote
                        field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        closed = True
                        break
                else:
                    field_chars.append(text[i])
                    i += 1

            if not closed:
                raise ValueError("Unclosed quoted field")

            # After closing quote, must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Invalid character after closing quote: {text[i]!r}")

            current_record.append("".join(field_chars))

            # Now consume the delimiter
            if i < n:
                if text[i] == ',':
                    i += 1
                    # If next is end of input or newline, we need another field
                    if i == n:
                        current_record.append("")
                        records.append(current_record)
                        break
                elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 2
                    if i == n:
                        break
                elif text[i] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 1
                    if i == n:
                        break
            else:
                records.append(current_record)
                break
        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))

            # Consume delimiter
            if i < n:
                if text[i] == ',':
                    i += 1
                    if i == n:
                        current_record.append("")
                        records.append(current_record)
                        break
                elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 2
                    if i == n:
                        break
                elif text[i] == '\n':
                    records.append(current_record)
                    current_record = []
                    i += 1
                    if i == n:
                        break
            else:
                records.append(current_record)
                break

    return records
