def parse_csv(text: str) -> list[list[str]]:
    """Parses a CSV string into a list of lists of strings."""
    if not text:
        return []

    result = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line and result:
            result[-1].append("")
            continue

        if not line:
            result.append([""])
            continue

        current_field = ""
        in_quotes = False
        quote_char = None
        for char in line:
            if char == '"':
                if in_quotes:
                    if char == quote_char:
                        in_quotes = False
                    else:
                        current_field += quote_char
                else:
                    in_quotes = True
                    quote_char = char
            elif char == ',' and not in_quotes:
                result.append([current_field])
                current_field = ""
            else:
                current_field += char

        if current_field:
            result.append([current_field])

    return result
