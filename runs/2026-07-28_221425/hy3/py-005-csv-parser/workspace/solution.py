def parse_csv(text: str) -> list[list[str]]:
    records = []
    n = len(text)
    i = 0

    def parse_field(start):
        i = start
        if i >= n:
            return '', i
        if text[i] == '"':
            i += 1
            chars = []
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        return ''.join(chars), i
                else:
                    chars.append(text[i])
                    i += 1
            raise ValueError("unterminated quoted field")
        else:
            chars = []
            while i < n:
                c = text[i]
                if c == ',':
                    break
                if c == '\n':
                    break
                if c == '\r' and i + 1 < n and text[i + 1] == '\n':
                    break
                chars.append(c)
                i += 1
            return ''.join(chars), i

    while i < n:
        current_record = []
        while True:
            field, i = parse_field(i)
            current_record.append(field)
            if i >= n:
                break
            c = text[i]
            if c == ',':
                i += 1
                continue
            if c == '\n':
                i += 1
                break
            if c == '\r' and i + 1 < n and text[i + 1] == '\n':
                i += 2
                break
            raise ValueError("invalid character after field")
        records.append(current_record)
    return records
