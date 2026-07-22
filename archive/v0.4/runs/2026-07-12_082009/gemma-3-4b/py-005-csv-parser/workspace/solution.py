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
        if in_quotes:
            i = 0
            while i < len(line):
                char = line[i]
                if char == quote_char and i > 0 and line[i - 1] != '\\':
                    in_quotes = False
                    current_field += quote_char
                    break
                elif char == '"' and not in_quotes:
                    quote_char = char
                elif char == '\\':
                    if i + 1 < len(line):
                        next_char = line[i + 1]
                        if next_char == '"':
                            current_field += '"'
                        else:
                            raise ValueError("Invalid escape sequence")
                        i += 2
                    else:
                        raise ValueError("Malformed CSV: Unexpected end of quote")

                else:
                    current_field += char
                    i += 1
            if in_quotes:
                raise ValueError("Unclosed quotes")
        else:
            parts = line.split(',')
            fields = []
            for part in parts:
                if part == "":
                    fields.append("")
                else:
                    fields.append(part)

            result.append(fields)

    return result
