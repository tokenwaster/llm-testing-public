def parse_csv(text: str) -> list[list[str]]:
    """Parses a CSV string according to RFC 4180."""
    if not text:
        return []

    lines = text.splitlines()
    result = []
    for line in lines:
        line = line.strip()
        if not line and result:
            result.append([])
            continue

        if not line:
            continue

        fields = []
        in_quote = False
        current_field = ""
        i = 0
        while i < len(line):
            char = line[i]

            if in_quote:
                if char == '"':
                    if i > 0 and line[i - 1] == '"':
                        current_field += '"'
                    elif i + 1 < len(line) and line[i + 1] == '"':
                        current_field += '""'
                    else:
                        raise ValueError("Unclosed quote")
                    in_quote = False
                else:
                    current_field += char
            else:
                if char == '"':
                    in_quote = True
                elif char == ',':
                    fields.append(current_field)
                    current_field = ""
                else:
                    current_field += char

            i += 1

        fields.append(current_field)
        result.append(fields)

    return result
