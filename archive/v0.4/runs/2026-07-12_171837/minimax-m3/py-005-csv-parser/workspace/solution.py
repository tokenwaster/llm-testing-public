def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC 4180-style rules."""
    records = []
    record = []
    field_chars = []
    in_quotes = False
    after_closing_quote = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]
        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')
                    i += 2
                else:
                    in_quotes = False
                    after_closing_quote = True
                    i += 1
            else:
                field_chars.append(c)
                i += 1
        elif after_closing_quote:
            if c == ',':
                record.append(''.join(field_chars))
                field_chars = []
                after_closing_quote = False
                i += 1
            elif c == '\r':
                record.append(''.join(field_chars))
                records.append(record)
                record = []
                field_chars = []
                after_closing_quote = False
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
            elif c == '\n':
                record.append(''.join(field_chars))
                records.append(record)
                record = []
                field_chars = []
                after_closing_quote = False
                i += 1
            else:
                raise ValueError(
                    f"Unexpected character {c!r} after closing quote at position {i}"
                )
        else:
            if c == '"' and len(field_chars) == 0:
                in_quotes = True
                i += 1
            elif c == ',':
                record.append(''.join(field_chars))
                field_chars = []
                i += 1
            elif c == '\r':
                record.append(''.join(field_chars))
                records.append(record)
                record = []
                field_chars = []
                if i + 1 < n and text[i + 1] == '\n':
                    i += 2
                else:
                    i += 1
            elif c == '\n':
                record.append(''.join(field_chars))
                records.append(record)
                record = []
                field_chars = []
                i += 1
            else:
                field_chars.append(c)
                i += 1

    if in_quotes:
        raise ValueError("Unclosed quote in input")

    if after_closing_quote:
        record.append(''.join(field_chars))
        records.append(record)
        return records

    if field_chars or record:
        record.append(''.join(field_chars))
        records.append(record)

    return records
