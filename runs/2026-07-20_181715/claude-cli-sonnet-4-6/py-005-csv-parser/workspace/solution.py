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
            # End of input: finish current record
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
                    # Check for escaped quote or end of field
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
            # After closing quote: must be comma, newline, or EOF
            if i == n:
                current_record.append("".join(field_chars))
                records.append(current_record)
                break
            elif text[i] == ',':
                current_record.append("".join(field_chars))
                i += 1
                # If next is end of input, there's a trailing empty field
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append("".join(field_chars))
                records.append(current_record)
                current_record = []
                i += 2
                if i == n:
                    break
            elif text[i] == '\n':
                current_record.append("".join(field_chars))
                records.append(current_record)
                current_record = []
                i += 1
                if i == n:
                    break
            else:
                raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")
        elif ch == ',':
            # Empty field before comma
            current_record.append("")
            i += 1
            if i == n:
                # Trailing comma means one more empty field
                current_record.append("")
                records.append(current_record)
                break
        elif ch == '\r' and i + 1 < n and text[i + 1] == '\n':
            current_record.append("")
            records.append(current_record)
            current_record = []
            i += 2
            if i == n:
                break
        elif ch == '\n':
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
            field = "".join(field_chars)
            if i == n:
                current_record.append(field)
                records.append(current_record)
                break
            elif text[i] == ',':
                current_record.append(field)
                i += 1
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_record.append(field)
                records.append(current_record)
                current_record = []
                i += 2
                if i == n:
                    break
            elif text[i] == '\n':
                current_record.append(field)
                records.append(current_record)
                current_record = []
                i += 1
                if i == n:
                    break

    return records
