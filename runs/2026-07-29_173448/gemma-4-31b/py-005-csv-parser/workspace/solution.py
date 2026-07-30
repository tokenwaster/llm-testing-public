def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string according to RFC-4180 guidelines from scratch.
    """
    if not text:
        return []

    rows = []
    i = 0
    n = len(text)

    while i < n:
        row = []
        # Process fields within a single record
        while True:
            # Check if the field is quoted (must start with a double-quote)
            if i < n and text[i] == '"':
                i += 1  # Skip opening quote
                field_chars = []
                while True:
                    if i >= n:
                        raise ValueError("Unclosed quote")
                    if text[i] == '"':
                        # Check for escaped double-quotes ("")
                        if i + 1 < n and text[i + 1] == '"':
                            field_chars.append('"')
                            i += 2
                        else:
                            # End of quoted field
                            i += 1  # Skip closing quote
                            break
                    else:
                        field_chars.append(text[i])
                        i += 1
                row.append("".join(field_chars))
            else:
                # Literal field parsing (everything until comma or newline)
                field_chars = []
                while i < n and text[i] not in (',', '\n', '\r'):
                    field_chars.append(text[i])
                    i += 1
                row.append("".join(field_chars))

            # Determine what follows the field: another field, end of record, or EOF
            if i < n and text[i] == ',':
                i += 1  # Move to next field in current row
                continue
            elif i < n and (text[i] == '\n' or text[i] == '\r'):
                # Record separator: handle \n, \r, or \r\n
                if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                break  # Move to the next record in outer loop
            elif i < n:
                # Malformed input: characters found immediately after a closing quote
                raise ValueError("Invalid character after closing quote")
            else:
                # End of string reached
                break

        rows.append(row)

    return rows
