def parse_csv(text: str) -> list[list[str]]:
    """Parses CSV text according to RFC-4180."""
    if not text:
        return []

    result = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line and result:
            result.append([])
            continue

        if not line:
            continue  # Skip completely empty lines

        fields = []
        current_field = ""
        in_quotes = False
        quote_char = None

        for char in line:
            if char == '"':
                if in_quotes:
                    if char == '"':
                        current_field += '"'
                    else:
                        quote_char = char
                        current_field += char
                    in_quotes = False
                else:
                    in_quotes = True
                    current_field += char
            elif char == ',' and not in_quotes:
                fields.append(current_field)
                current_field = ""
            elif char == '\n' or char == '\r':
                # Ignore extra newlines within a field, but treat \r\n as newline
                continue
            else:
                current_field += char

        fields.append(current_field)

        if quote_char is None and line.endswith('"'): # Handle trailing quote case (rare)
           raise ValueError("Unclosed quote")
        elif quote_char is not None and line.endswith(quote_char):
            raise ValueError("Unclosed quote")


        result.append(fields)

    return result
