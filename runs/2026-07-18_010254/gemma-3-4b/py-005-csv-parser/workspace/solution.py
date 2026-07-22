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
            if line.startswith('"'):
                if quote_char != line[0]:
                    raise ValueError("Unmatched quotes")
                if line.endswith('"'):
                    in_quotes = False
                    current_field += line[1:-1]  # Remove quotes
                else:
                    current_field += line
            else:
                current_field += line
        else:
            parts = line.split(',')
            for part in parts:
                if part == "":
                    current_field = ""
                else:
                    current_field = part
            if current_field != "":
                result.append([current_field])

        if line.endswith('\r\n'):
            pass  # Handle both \n and \r\n
        elif line.endswith('\n'):
            pass #Handle only \n
        else:
            pass


    return result
