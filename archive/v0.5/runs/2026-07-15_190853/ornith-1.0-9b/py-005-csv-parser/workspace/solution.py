def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    i = 0
    n = len(text)

    while i < n:
        # Skip record separators (\r\n or \n, also standalone \r for robustness)
        if text[i] == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            continue

        if text[i] == '\n':
            i += 1
            continue

        # Parse a record (fields separated by commas)
        fields = []
        while True:
            field, i = _parse_field(text, n, i)
            fields.append(field)

            if i >= n:
                break

            if text[i] == ',':
                i += 1
            elif text[i] in ('\r', '\n'):
                # End of record (newline or carriage return)
                break
            else:
                raise ValueError(f"Unexpected character at position {i}")

        records.append(fields)

    return records


def _parse_field(text, n, i):
    if text[i] == '"':
        result = []
        i += 1
        while True:
            if i >= n:
                raise ValueError("Unclosed quote")
            if text[i] == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped double-quote → single "
                    result.append('"')
                    i += 2
                else:
                    # End of quoted field
                    i += 1
                    break
            elif text[i] in ('\r', '\n'):
                # Newlines are allowed inside quoted fields
                result.append(text[i])
                i += 1
            else:
                result.append(text[i])
                i += 1

        return ''.join(result), i

    else:
        # Unquoted field — stops at comma, \r, or \n
        result = []
        while i < n and text[i] not in (',', '\r', '\n'):
            result.append(text[i])
            i += 1

        return ''.join(result), i
