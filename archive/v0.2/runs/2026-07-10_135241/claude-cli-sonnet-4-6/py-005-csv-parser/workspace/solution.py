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
            # End of input after a record separator - don't add extra record
            # But we need to finalize the current record
            current_record.append("")
            records.append(current_record)
            break

        ch = text[i]

        if ch == '"':
            # Quoted field
            i += 1
            field_chars = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        # Escaped double quote
                        field_chars.append('"')
                        i += 2
                    else:
                        # Closing quote
                        i += 1
                        closed = True
                        break
                else:
                    field_chars.append(c)
                    i += 1

            if not closed:
                raise ValueError("Unclosed quoted field")

            # After closing quote, must be comma, newline, or EOF
            if i < n:
                c = text[i]
                if c == ',':
                    current_record.append("".join(field_chars))
                    i += 1
                    # Check if this comma is the last char (trailing comma means empty field follows)
                    if i == n:
                        current_record.append("")
                        records.append(current_record)
                        current_record = None
                        break
                elif c == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        i += 2
                    else:
                        i += 1
                    current_record.append("".join(field_chars))
                    records.append(current_record)
                    current_record = []
                    if i == n:
                        current_record = None
                        break
                elif c == '\n':
                    i += 1
                    current_record.append("".join(field_chars))
                    records.append(current_record)
                    current_record = []
                    if i == n:
                        current_record = None
                        break
                else:
                    raise ValueError(f"Invalid character after closing quote: {c!r}")
            else:
                # EOF after closing quote
                current_record.append("".join(field_chars))
                records.append(current_record)
                current_record = None
                break

        elif ch == ',':
            # Empty field
            current_record.append("")
            i += 1
            if i == n:
                # Trailing comma - one more empty field
                current_record.append("")
                records.append(current_record)
                current_record = None
                break

        elif ch == '\r':
            # Record separator
            current_record.append("")
            records.append(current_record)
            current_record = []
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            if i == n:
                # Trailing newline - don't create extra record
                current_record = None
                break

        elif ch == '\n':
            # Record separator
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 1
            if i == n:
                # Trailing newline - don't create extra record
                current_record = None
                break

        else:
            # Unquoted field - read until comma, newline, or EOF
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1

            field = "".join(field_chars)

            if i == n:
                current_record.append(field)
                records.append(current_record)
                current_record = None
                break
            elif text[i] == ',':
                current_record.append(field)
                i += 1
                if i == n:
                    # Trailing comma
                    current_record.append("")
                    records.append(current_record)
                    current_record = None
                    break
            elif text[i] == '\r':
                current_record.append(field)
                records.append(current_record)
                current_record = []
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                if i == n:
                    current_record = None
                    break
            elif text[i] == '\n':
                current_record.append(field)
                records.append(current_record)
                current_record = []
                i += 1
                if i == n:
                    current_record = None
                    break

    if current_record is not None and current_record:
        records.append(current_record)

    return records
