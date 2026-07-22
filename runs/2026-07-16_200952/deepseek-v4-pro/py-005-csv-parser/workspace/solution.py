def parse_csv(text: str) -> list[list[str]]:
    """
    Parse RFC-4180-style CSV from scratch.

    Returns a list of records, each a list of string fields.
    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    records = []
    fields = []
    current_field = ""
    in_quoted = False
    n = len(text)
    i = 0

    while i < n:
        c = text[i]

        if not in_quoted:
            if c == '"' and current_field == "":
                in_quoted = True
            elif c == ',':
                fields.append(current_field)
                current_field = ""
            elif c == '\n':
                fields.append(current_field)
                records.append(fields)
                fields = []
                current_field = ""
            elif c == '\r':
                # handle \r\n as a single record delimiter
                if i + 1 < n and text[i + 1] == '\n':
                    fields.append(current_field)
                    records.append(fields)
                    fields = []
                    current_field = ""
                    i += 1      # skip the '\n'
                else:
                    # standalone \r is a regular character
                    current_field += c
            else:
                current_field += c
        else:
            # inside a quoted field
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # escaped double quote -> one literal quote
                    current_field += '"'
                    i += 1
                else:
                    # closing quote
                    in_quoted = False
                    # validate the next character after the closing quote
                    if i + 1 < n:
                        nc = text[i + 1]
                        if nc not in (',', '\n', '\r'):
                            raise ValueError("Malformed CSV: characters after closing quote")
            else:
                # any other character, including commas, newlines, and \r
                current_field += c
        i += 1

    if in_quoted:
        raise ValueError("Malformed CSV: unclosed quote")

    # finalise the last record if it contains any data
    if fields or current_field:
        fields.append(current_field)
        records.append(fields)

    return records
