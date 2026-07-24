from __future__ import annotations

def parse_csv(text: str) -> list[list[str]]:
    n = len(text)
    i = 0
    records: list[list[str]] = []

    def parse_field(i: int):
        if i == n:
            return ("", i, "EOF")
        if text[i] == '"':
            i += 1
            chars: list[str] = []
            while i < n:
                ch = text[i]
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        i += 1
                        if i == n:
                            return ("".join(chars), i, "EOF")
                        if text[i] == ',':
                            i += 1
                            return ("".join(chars), i, ",")
                        if text[i] == '\n':
                            i += 1
                            return ("".join(chars), i, "\n")
                        if text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                            i += 2
                            return ("".join(chars), i, "\r\n")
                        raise ValueError("Characters after closing quote")
                else:
                    chars.append(ch)
                    i += 1
            raise ValueError("Unclosed quote")
        else:
            chars = []
            while i < n:
                ch = text[i]
                if ch == ',':
                    i += 1
                    return ("".join(chars), i, ",")
                if ch == '\n':
                    i += 1
                    return ("".join(chars), i, "\n")
                if ch == '\r' and i + 1 < n and text[i + 1] == '\n':
                    i += 2
                    return ("".join(chars), i, "\r\n")
                chars.append(ch)
                i += 1
            return ("".join(chars), i, "EOF")

    while i < n:
        fields: list[str] = []
        while True:
            field, i, term = parse_field(i)
            fields.append(field)
            if term == "EOF":
                records.append(fields)
                break
            if term == ",":
                continue
            records.append(fields)
            break

    return records
