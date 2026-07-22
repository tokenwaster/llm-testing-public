def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    fields = []
    field = ""
    i = 0
    n = len(text)
    in_quotes = False
    has_content = False

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                # Could be escaped quote or closing quote
                if i + 1 < n and text[i + 1] == '"':
                    field += '"'
                    has_content = True
                    i += 2
                    continue
                else:
                    # Closing quote — verify next char is comma, newline, \r, or EOF
                    if i + 1 < n and text[i + 1] not in (',', '\n', '\r'):
                        raise ValueError("Invalid character after closing quote")
                    in_quotes = False
                    has_content = True
                    i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                field += '\r\n'
                has_content = True
                i += 2
            elif c == '\n':
                field += '\n'
                has_content = True
                i += 1
            else:
                field += c
                has_content = True
                i += 1
        else:
            if c == ',':
                fields.append(field)
                field = ""
                has_content = True
                i += 1
            elif c == '\r' and i + 1 < n and text[i + 1] == '\n':
                fields.append(field)
                records.append(fields)
                fields = []
                field = ""
                has_content = False
                i += 2
            elif c == '\n':
                fields.append(field)
                records.append(fields)
                fields = []
                field = ""
                has_content = False
                i += 1
            elif c == '"' and not field:
                # Field starts with a quote → enter quoted mode
                in_quotes = True
                has_content = True
                i += 1
            else:
                field += c
                has_content = True
                i += 1

    if in_quotes:
        raise ValueError("Unclosed quote")

    # Finalize the last record if any content was consumed
    if has_content:
        fields.append(field)
        records.append(fields)

    return records
