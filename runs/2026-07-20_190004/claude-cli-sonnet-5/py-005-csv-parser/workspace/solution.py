def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)
    i = 0
    records = []
    row = []

    while True:
        if i < n and text[i] == '"':
            i += 1
            chars = []
            closed = False
            while i < n:
                c = text[i]
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                        continue
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
                term = None
            elif text[i] == ',':
                term = ','
                i += 1
            elif text[i] == '\n':
                term = '\n'
                i += 1
            elif text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                term = '\n'
                i += 2
            else:
                raise ValueError("unexpected character after closing quote")
        else:
            chars = []
            while True:
                if i >= n:
                    break
                c = text[i]
                if c == ',' or c == '\n':
                    break
                if c == '\r':
                    if i + 1 < n and text[i + 1] == '\n':
                        break
                    else:
                        chars.append(c)
                        i += 1
                        continue
                chars.append(c)
                i += 1
            field = ''.join(chars)

            if i >= n:
                term = None
            elif text[i] == ',':
                term = ','
                i += 1
            elif text[i] == '\n':
                term = '\n'
                i += 1
            else:  # text[i] == '\r' followed by '\n'
                term = '\n'
                i += 2

        row.append(field)

        if term is None:
            records.append(row)
            break
        elif term == ',':
            continue
        else:  # newline terminator
            records.append(row)
            row = []
            if i >= n:
                break
            continue

    return records
