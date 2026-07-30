def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    i = 0
    n = len(text)
    records: list[list[str]] = []
    record: list[str] = []

    while True:
        if i < n and text[i] == '"':
            i += 1
            chars: list[str] = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        closed = True
                        break
                else:
                    chars.append(c)
                    i += 1
            if not closed:
                raise ValueError("unterminated quoted field")
            field = ''.join(chars)

            if i >= n:
                terminator = 'eof'
            elif text[i] == ',':
                terminator = 'comma'
                i += 1
            elif text[i] == '\n':
                terminator = 'newline'
                i += 1
            elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                terminator = 'newline'
                i += 2
            else:
                raise ValueError("unexpected characters after closing quote")
        else:
            start = i
            while i < n and text[i] not in (',', '\n', '\r'):
                i += 1
            field = text[start:i]

            if i >= n:
                terminator = 'eof'
            elif text[i] == ',':
                terminator = 'comma'
                i += 1
            elif text[i] == '\n':
                terminator = 'newline'
                i += 1
            else:  # text[i] == '\r'
                if i + 1 < n and text[i + 1] == '\n':
                    terminator = 'newline'
                    i += 2
                else:
                    terminator = 'newline'
                    i += 1

        record.append(field)

        if terminator == 'comma':
            continue
        elif terminator == 'newline':
            records.append(record)
            record = []
            if i >= n:
                break
        else:  # eof
            records.append(record)
            break

    return records
