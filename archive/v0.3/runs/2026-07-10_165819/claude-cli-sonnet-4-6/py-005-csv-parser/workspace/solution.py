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
            # End of input - finish current record
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
                        # Escaped quote
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
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Invalid character after closing quote: {text[i]!r}")

            current_record.append("".join(field_chars))

            if i == n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                # Check if next is end of input (trailing comma means empty field follows)
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                records.append(current_record)
                current_record = []
                if i == n:
                    break
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
                if i == n:
                    break

        elif ch == ',':
            # Empty field followed by comma
            current_record.append("")
            i += 1
            if i == n:
                current_record.append("")
                records.append(current_record)
                break

        elif ch == '\r':
            # End of record
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 1
            if i < n and text[i] == '\n':
                i += 1
            if i == n:
                break

        elif ch == '\n':
            # End of record
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 1
            if i == n:
                break

        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1

            current_record.append("".join(field_chars))

            if i == n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r':
                records.append(current_record)
                current_record = []
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                if i == n:
                    break
            elif text[i] == '\n':
                records.append(current_record)
                current_record = []
                i += 1
                if i == n:
                    break

    # Handle trailing newline: if last record is single empty field added due to trailing newline
    # We need to remove it
    if records:
        # Check if original text ended with \n or \r\n
        ends_with_newline = text.endswith('\n') or text.endswith('\r\n')
        if ends_with_newline:
            # The last record was added because of the newline terminator
            # If it's a single empty string, it's the trailing newline artifact
            if records[-1] == ['']:
                records.pop()

    return records
