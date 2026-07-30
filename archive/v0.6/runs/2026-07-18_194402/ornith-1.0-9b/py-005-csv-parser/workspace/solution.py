def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    seen_content = False

    while i < len(text):
        # Check for line ending (\r\n or standalone \r)
        if text[i] == '\r':
            if i + 1 < len(text) and text[i+1] == '\n':
                i += 2
            else:
                i += 1
            if current_record:
                records.append(current_record)
                current_record = []
            elif seen_content:
                # Empty line in the middle - one record with single empty field
                records.append([""])
                current_record = []
            continue

        # Check for line ending (\n)
        if text[i] == '\n':
            i += 1
            if current_record:
                records.append(current_record)
                current_record = []
            elif seen_content:
                # Empty line in the middle - one record with single empty field
                records.append([""])
                current_record = []
            continue

        # Field separator (comma)
        if text[i] == ',':
            i += 1
            continue

        # Parse field
        field = ''
        if text[i] == '"':
            # Quoted field
            seen_content = True
            i += 1
            while i < len(text):
                if text[i] == '"':
                    if i + 1 < len(text) and text[i+1] == '"':
                        field += '"'
                        i += 2
                    else:
                        # Closing quote - check what follows
                        i += 1
                        break
                else:
                    field += text[i]
                    i += 1
            else:
                raise ValueError("Unterminated quoted field")

            # Check that after closing quote, next char is comma, newline, or EOF
            if i < len(text) and text[i] not in (',', '\n', '\r'):
                raise ValueError(f"Unexpected character '{text[i]}' after closing quote")

            current_record.append(field)
        else:
            # Unquoted field - read until comma, newline, or CR
            seen_content = True
            while i < len(text) and text[i] not in (',', '\n', '\r'):
                field += text[i]
                i += 1
            current_record.append(field)

    if current_record:
        records.append(current_record)

    # Remove trailing empty record caused by trailing newline(s)
    while records and records[-1] == [""]:
        records.pop()

    return records
