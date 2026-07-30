def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string based on RFC-4180 rules from scratch.
    Returns a list of lists of strings representing the rows and fields.
    """
    if not text:
        return []

    res = []
    curr_row = []
    curr_field = ""
    i = 0
    n = len(text)
    in_quotes = False

    while i < n:
        c = text[i]
        if not in_quotes:
            if c == '"':
                # Quotes only have special meaning if the field starts with a quote.
                is_start = (i == 0 or text[i-1] in (',', '\n', '\r'))
                if is_start:
                    in_quotes = True
                else:
                    curr_field += c
            elif c == ',':
                # End of a field.
                curr_row.append(curr_field)
                curr_field = ""
            elif c in ('\n', '\r'):
                # Handle \r\n as a single record separator.
                if c == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                curr_row.append(curr_field)
                res.append(curr_row)
                curr_row = []
                curr_field = ""
            else:
                # Normal character in a non-quoted field.
                curr_field += c
        else:  # Currently inside a quoted field.
            if c == '"':
                # Check for doubled double-quotes ("") which decodes to one (").
                if i + 1 < n and text[i+1] == '"':
                    curr_field += '"'
                    i += 1
                else:
                    # Closing quote.
                    in_quotes = False
                    # Rule check: characters after a closing quote must be comma, newline/carriage return, or EOF.
                    if i + 1 < n:
                        next_c = text[i+1]
                        if next_c not in (',', '\n', '\r'):
                            raise ValueError("Malformed input")
            else:
                # Standard character within quotes including commas and newlines.
                curr_field += c
        i += 1

    if in_quotes:
        raise ValueError("Unclosed quote")

    # Handle remaining content after the loop.
    # If text ended with a newline, we should not add an extra record (trailing newline rule).
    # However, if it ends with a field or a comma, we must append what's left.
    if curr_field or (i > 0 and text[i-1] == ','):
        curr_row.append(curr_field)
        res.append(curr_row)

    return res
