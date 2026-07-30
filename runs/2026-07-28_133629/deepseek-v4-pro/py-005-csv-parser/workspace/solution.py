def parse_csv(text: str) -> list[list[str]]:
    """
    Parse CSV text according to RFC 4180 rules.

    Args:
        text: The CSV input as a string.

    Returns:
        A list of records, each a list of field strings.

    Raises:
        ValueError: If the input is malformed.
    """
    # Strip a trailing newline (which doesn't create an extra record)
    if text.endswith('\r\n'):
        text = text[:-2]
    elif text.endswith('\n'):
        text = text[:-1]

    if text == '':
        return []

    records = []
    current_fields = []
    current_chars = []
    in_quoted = False
    n = len(text)
    i = 0

    while i < n:
        ch = text[i]

        if not in_quoted:
            if ch == '"':
                # Quoted field only if it starts the field
                if not current_chars:
                    in_quoted = True
                    i += 1
                    continue
                else:
                    current_chars.append('"')
                    i += 1
                    continue
            elif ch == ',':
                current_fields.append(''.join(current_chars))
                current_chars = []
                i += 1
                continue
            elif ch == '\r':
                # Check for \r\n (Windows line break)
                if i + 1 < n and text[i + 1] == '\n':
                    current_fields.append(''.join(current_chars))
                    current_chars = []
                    records.append(current_fields)
                    current_fields = []
                    i += 2
                    continue
                else:
                    # Bare \r is literal (not a line break)
                    current_chars.append('\r')
                    i += 1
                    continue
            elif ch == '\n':
                # Unix line break
                current_fields.append(''.join(current_chars))
                current_chars = []
                records.append(current_fields)
                current_fields = []
                i += 1
                continue
            else:
                current_chars.append(ch)
                i += 1
                continue
        else:  # Inside a quoted field
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped double-quote ("" -> ")
                    current_chars.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote
                    in_quoted = False
                    i += 1
                    # Character after closing quote must be valid
                    if i < n:
                        next_ch = text[i]
                        if next_ch == ',' or next_ch == '\n':
                            pass
                        elif next_ch == '\r':
                            if i + 1 < n and text[i + 1] == '\n':
                                pass
                            else:
                                raise ValueError("Invalid character after closing quote")
                        else:
                            raise ValueError("Invalid character after closing quote")
                    continue
            else:
                current_chars.append(ch)
                i += 1
                continue

    if in_quoted:
        raise ValueError("Unclosed quoted field")

    # Append the final field and record, if any
    if current_chars or current_fields:
        current_fields.append(''.join(current_chars))
        records.append(current_fields)

    return records
