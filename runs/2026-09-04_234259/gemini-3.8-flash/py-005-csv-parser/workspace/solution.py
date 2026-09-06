def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)
    i = 0
    records = []
    current_record = []

    while i < n:
        if text[i] == '"':
            # Quoted field
            i += 1
            chars = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        closed = True
                        i += 1
                        break
                else:
                    chars.append(text[i])
                    i += 1

            if not closed:
                raise ValueError("Unclosed quote in CSV")

            field = "".join(chars)

            # Characters after a closing quote must be comma, newline, or EOF
            if not (i == n or text[i] == ',' or text[i] == '\n' or text[i:i+2] == '\r\n'):
                raise ValueError(f"Unexpected character after closing quote at index {i}: {text[i]!r}")
        else:
            # Unquoted field
            start = i
            while i < n:
                if text[i] == ',' or text[i] == '\n' or text[i:i+2] == '\r\n':
                    break
                i += 1
            field = text[start:i]

        current_record.append(field)

        if i == n:
            records.append(current_record)
            current_record = []
            break
        elif text[i] == ',':
            i += 1
            if i == n:
                # Trailing comma at EOF produces an empty field
                current_record.append("")
                records.append(current_record)
                current_record = []
                break
        elif text[i:i+2] == '\r\n':
            records.append(current_record)
            current_record = []
            i += 2
        elif text[i] == '\n':
            records.append(current_record)
            current_record = []
            i += 1

    return records
