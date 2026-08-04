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

        ch = text[i]

        # Quoted field
        if ch == '"':
            i += 1  # skip opening quote
            field_chars = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    # Check for escaped quote ""
                    if i + 1 < n and text[i + 1] == '"':
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

            # Now handle delimiter
            if i == n:
                records.append(current_record)
                break
            elif text[i] == ',':
                i += 1
                # If next char is end of input or newline, there's another empty field coming
                # handled by next loop iteration
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

        # Unquoted field
        else:
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
                # If at end of input after comma, add empty field
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
                # trailing newline: if at end, don't create extra record
                if i == n:
                    break
            elif text[i] == '\n':
                i += 1
                records.append(current_record)
                current_record = []
                # trailing newline: if at end, don't create extra record
                if i == n:
                    break

    return records
