def parse_csv(text: str) -> list[list[str]]:
    """Parses a CSV string into a list of lists of strings."""

    if not text:
        return []

    result = []
    lines = text.splitlines()
    in_quotes = False
    current_field = ""
    quote_char = None

    for line in lines:
        current_record = []
        i = 0
        while i < len(line):
            if not in_quotes and line[i] == '"':
                if i > 0 and line[i - 1] != '\\':
                    in_quotes = True
                    quote_char = line[i]
                    current_field += line[i]
                    i += 1
                else:
                    # Escaped quote, treat as normal character
                    current_field += line[i]
                    i += 1
            elif in_quotes and line[i] == quote_char:
                in_quotes = False
                current_field += line[i]
                i += 1
            elif not in_quotes and line[i] == ',':
                current_record.append(current_field)
                current_field = ""
                i += 1
            else:
                current_field += line[i]
                i += 1

        current_record.append(current_field)
        if current_record:
            result.append(current_record)

    return result
