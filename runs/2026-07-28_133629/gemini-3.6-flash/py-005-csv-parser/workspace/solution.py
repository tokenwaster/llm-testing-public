def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    i = 0
    n = len(text)

    while i < n:
        current_row = []
        while True:
            if i < n and text[i] == '"':
                # Quoted field
                i += 1  # consume opening quote
                field_chars = []
                closed = False
                while i < n:
                    if text[i] == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            field_chars.append('"')
                            i += 2
                        else:
                            i += 1
                            closed = True
                            break
                    else:
                        field_chars.append(text[i])
                        i += 1

                if not closed:
                    raise ValueError("Unclosed double quote in CSV field")

                current_row.append("".join(field_chars))

                if i == n:
                    records.append(current_row)
                    break
                elif text[i] == ',':
                    i += 1
                    if i == n:
                        current_row.append("")
                        records.append(current_row)
                        break
                elif text[i : i + 2] == '\r\n':
                    i += 2
                    records.append(current_row)
                    break
                elif text[i] == '\n':
                    i += 1
                    records.append(current_row)
                    break
                else:
                    raise ValueError(
                        f"Unexpected character {text[i]!r} after closing quote at position {i}"
                    )

            else:
                # Unquoted field
                field_chars = []
                while i < n:
                    if text[i] == ',':
                        break
                    elif text[i : i + 2] == '\r\n':
                        break
                    elif text[i] == '\n':
                        break
                    else:
                        field_chars.append(text[i])
                        i += 1

                current_row.append("".join(field_chars))

                if i == n:
                    records.append(current_row)
                    break
                elif text[i] == ',':
                    i += 1
                    if i == n:
                        current_row.append("")
                        records.append(current_row)
                        break
                elif text[i : i + 2] == '\r\n':
                    i += 2
                    records.append(current_row)
                    break
                elif text[i] == '\n':
                    i += 1
                    records.append(current_row)
                    break

    return records
