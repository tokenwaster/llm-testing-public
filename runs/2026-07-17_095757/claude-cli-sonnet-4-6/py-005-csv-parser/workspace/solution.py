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
            # We only get here if we need to finalize
            current_record.append("")
            records.append(current_record)
            break

        ch = text[i]

        if ch == '"':
            # Quoted field
            i += 1
            field_chars = []
            while True:
                if i >= n:
                    raise ValueError("Unclosed quoted field")
                c = text[i]
                if c == '"':
                    # Check for doubled quote or end of field
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

            field = "".join(field_chars)

            # After closing quote, must be comma, newline, or EOF
            if i < n and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Unexpected character after closing quote: {text[i]!r}")

            current_record.append(field)

            if i >= n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                # If next is end of input, we have a trailing empty field
                if i >= n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                records.append(current_record)
                current_record = []
                if i >= n:
                    break
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
                if i >= n:
                    break

        elif ch == '\r' or ch == '\n':
            # End of record (empty field or end of record)
            current_record.append("")
            records.append(current_record)
            current_record = []
            if ch == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
            else:
                i += 1
            # If this was a trailing newline (end of input), don't add extra record
            if i >= n:
                break

        elif ch == ',':
            # Empty field before comma
            current_record.append("")
            i += 1
            # If next is end of input, trailing empty field
            if i >= n:
                current_record.append("")
                records.append(current_record)
                break

        else:
            # Unquoted field
            field_chars = []
            while i < n and text[i] not in (',', '\n', '\r'):
                field_chars.append(text[i])
                i += 1

            field = "".join(field_chars)
            current_record.append(field)

            if i >= n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                # If next is end of input, trailing empty field
                if i >= n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1
                records.append(current_record)
                current_record = []
                if i >= n:
                    break
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
                if i >= n:
                    break

    return records
