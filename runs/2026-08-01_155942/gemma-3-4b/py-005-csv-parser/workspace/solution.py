def parse_csv(text: str) -> list[list[str]]:
    """Parses a CSV string into a list of lists of strings."""

    if not text:
        return []

    lines = text.splitlines()
    result = []
    for line in lines:
        row = []
        in_quotes = False
        current_field = ""
        i = 0
        while i < len(line):
            if line[i] == '"':
                if in_quotes:
                    if i + 1 < len(line) and line[i+1] == '"':
                        current_field += '""'
                        i += 1
                    else:
                        in_quotes = False
                else:
                    in_quotes = True
            elif line[i] == ',' and not in_quotes:
                row.append(current_field)
                current_field = ""
            else:
                current_field += line[i]
            i += 1

        row.append(current_field)
        result.append(row)

    return result
