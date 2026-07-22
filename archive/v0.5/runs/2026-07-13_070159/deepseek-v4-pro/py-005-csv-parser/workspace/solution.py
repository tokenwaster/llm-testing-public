def parse_csv(text: str) -> list[list[str]]:
    """
    Parse RFC-4180-style CSV from scratch.
    
    Args:
        text: The CSV string to parse.
        
    Returns:
        A list of records, each a list of field strings.
        
    Raises:
        ValueError: If the input is malformed (unclosed quote or unexpected
                    characters after a closing quote).
    """
    if not text:
        return []

    result = []
    current_record = []
    current_field = []
    in_quotes = False
    has_record = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if not in_quotes:
            if c == '"':
                # Quote only has special meaning at the start of a field
                if len(current_field) == 0:
                    in_quotes = True
                    has_record = True
                else:
                    current_field.append(c)
                    has_record = True
            elif c == ',':
                current_record.append(''.join(current_field))
                current_field = []
                has_record = True
            elif c == '\n':
                current_record.append(''.join(current_field))
                result.append(current_record)
                current_record = []
                current_field = []
                has_record = False
            elif c == '\r':
                # Check for \r\n (CRLF)
                if i + 1 < n and text[i + 1] == '\n':
                    current_record.append(''.join(current_field))
                    result.append(current_record)
                    current_record = []
                    current_field = []
                    has_record = False
                    i += 1  # skip the \n
                else:
                    # Lone \r is a regular character
                    current_field.append(c)
                    has_record = True
            else:
                current_field.append(c)
                has_record = True
        else:  # in_quotes
            if c == '"':
                # Check for escaped quote (doubled)
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 1
                else:
                    # Closing quote
                    in_quotes = False
                    # Validate characters after closing quote
                    if i + 1 < n:
                        nxt = text[i + 1]
                        if nxt == ',' or nxt == '\n':
                            pass
                        elif nxt == '\r':
                            # \r is only allowed if part of \r\n
                            if i + 2 < n and text[i + 2] == '\n':
                                pass
                            else:
                                raise ValueError(
                                    "Unexpected character after closing quote"
                                )
                        else:
                            raise ValueError(
                                "Unexpected character after closing quote"
                            )
            else:
                current_field.append(c)
        i += 1

    if in_quotes:
        raise ValueError("Unclosed quote")

    if has_record:
        current_record.append(''.join(current_field))
        result.append(current_record)

    return result
