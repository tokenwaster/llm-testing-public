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
            # End of input: finish last record
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
                    # Could be escaped quote or end of field
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # End of quoted field
                        i += 1
                        break
                else:
                    field_chars.append(c)
                    i += 1
            # After closing quote, must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
            current_record.append("".join(field_chars))
        elif ch == ',':
            # Empty field before comma
            current_record.append("")
        elif ch == '\r':
            # \r\n or bare \r as record separator
            current_record.append("")
            records.append(current_record)
            current_record = []
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            # Check for trailing newline at end
            if i == n:
                break
            continue
        elif ch == '\n':
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 1
            # Check for trailing newline at end
            if i == n:
                break
            continue
        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1
            current_record.append("".join(field_chars))
            # Don't advance i here; let the loop handle delimiter
            continue

        # After appending a field (quoted or empty-before-comma cases)
        if i < n:
            c = text[i]
            if c == ',':
                i += 1
                # If comma is last char, there's a trailing empty field
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif c == '\r':
                records.append(current_record)
                current_record = []
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
                if i == n:
                    break
            elif c == '\n':
                records.append(current_record)
                current_record = []
                i += 1
                if i == n:
                    break
        else:
            # EOF after field
            records.append(current_record)
            break

    return records
