def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    current_record: list[str] = []
    i = 0
    n = len(text)

    def read_quoted_field() -> str:
        nonlocal i
        i += 1  # skip opening quote
        chars: list[str] = []
        while i < n:
            c = text[i]
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped double-quote
                    chars.append('"')
                    i += 2
                else:
                    # Closing quote
                    i += 1
                    # Character after closing quote must be comma, newline, or EOF
                    if i < n:
                        if text[i] == ',' or text[i] == '\n':
                            pass  # valid; outer loop will consume
                        elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                            pass  # valid \r\n; outer loop will consume
                        else:
                            raise ValueError(
                                f"Unexpected character after closing quote at position {i}: {text[i]!r}"
                            )
                    return ''.join(chars)
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                chars.append('\r')
                chars.append('\n')
                i += 2
            else:
                chars.append(c)
                i += 1
        raise ValueError("Unclosed quoted field: reached end of input without closing quote")

    def read_unquoted_field() -> str:
        nonlocal i
        start = i
        while i < n:
            c = text[i]
            if c == ',' or c == '\n':
                break
            if c == '\r' and i + 1 < n and text[i + 1] == '\n':
                break  # stop before \r\n record separator
            i += 1
        return text[start:i]

    while i < n:
        # Read the next field
        if text[i] == '"':
            field = read_quoted_field()
        else:
            field = read_unquoted_field()

        current_record.append(field)

        if i >= n:
            # EOF reached inside or right after the field
            records.append(current_record)
            current_record = []
            break
        elif text[i] == ',':
            i += 1  # consume comma; next iteration reads the following field
        elif text[i] == '\n':
            i += 1
            records.append(current_record)
            current_record = []
        elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
            i += 2
            records.append(current_record)
            current_record = []

    # If the loop exited after consuming a comma (i == n), there is a
    # trailing empty field that was never read.
    if current_record:
        current_record.append('')
        records.append(current_record)

    return records
