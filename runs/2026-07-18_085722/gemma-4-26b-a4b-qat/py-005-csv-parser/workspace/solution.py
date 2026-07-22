def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    rows = []
    current_row = []
    current_field = []
    in_quotes = False
    at_start_of_field = True
    last_was_newline = False
    n = len(text)
    i = 0

    while i < n:
        char = text[i]
        if in_quotes:
            if char == '"':
                if i + 1 < n and text[i + 1] == '"':
                    current_field.append('"')
                    i += 1
                else:
                    in_quotes = False
                    at_start_of_field = False
                    if i + 1 < n:
                        next_char = text[i + 1]
                        if next_char == ',':
                            pass
                        elif next_char == '\n':
                            pass
                        elif next_char == '\r':
                            if i + 2 < n and text[i + 2] == '\n':
                                pass
                            else:
                                raise ValueError("Malformed CSV")
                        else:
                            raise ValueError("Malformed CSV")
            else:
                current_field.append(char)
        else:
            if char == '"' and at_start_of_field:
                in_quotes = True
                at_start_of_field = False
            elif char == ',':
                current_row.append("".join(current_field))
                current_field = []
                at_start_of_field = True
            elif char == '\r' and i + 1 < n and text[i + 1] == '\n':
                current_row.append("".join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                at_start_of_field = True
                last_was_newline = True
                i += 1
            elif char == '\n':
                current_row.append("".join(current_field))
                rows.append(current_row)
                current_row = []
                current_field = []
                at_start_of_field = True
                last_was_newline = True
            else:
                current_field.append(char)
                at_start_of_field = False
        i += 1

    if last_was_newline:
        if current_row or current_field:
            rows.append(current_row + ["".join(current_field)])
    else:
        rows.append(current_row + ["".join(current_field)])
    
    return rows
