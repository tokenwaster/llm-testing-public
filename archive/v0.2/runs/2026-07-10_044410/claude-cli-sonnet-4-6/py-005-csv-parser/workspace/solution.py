def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i <= n:
        # At start of a field
        if i == n:
            # End of input: finalize current record
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

            if i >= n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                # Check if next char starts a new field (loop continues)
                # But if we're at end after comma, add empty field
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                # End of record
                records.append(current_record)
                current_record = []
                if i == n:
                    # Trailing newline: no extra record
                    break
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
                if i == n:
                    # Trailing newline: no extra record
                    break

        elif ch == '\r':
            # Empty field at end of record
            current_record.append("")
            i += 1
            if i < n and text[i] == '\n':
                i += 1
            records.append(current_record)
            current_record = []
            if i == n:
                break

        elif ch == '\n':
            # Empty field at end of record
            current_record.append("")
            i += 1
            records.append(current_record)
            current_record = []
            if i == n:
                break

        elif ch == ',':
            # Empty field before comma
            current_record.append("")
            i += 1
            if i == n:
                current_record.append("")
                records.append(current_record)
                break

        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))

            if i >= n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
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

    return records
