def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV text according to RFC-4180-style rules.

    Fields are separated by commas, records by "\\n" or "\\r\\n". A field
    that starts with a double quote is a quoted field: it may contain
    commas and newlines, and a doubled quote ("") decodes to one quote.
    Raises ValueError on malformed input.
    """
    records: list[list[str]] = []
    n = len(text)
    i = 0

    while i < n:
        record: list[str] = []
        while True:
            # --- Parse a single field ---
            if text[i] == '"':
                # Quoted field.
                i += 1
                chars: list[str] = []
                while True:
                    if i >= n:
                        raise ValueError("unterminated quoted field")
                    c = text[i]
                    if c == '"':
                        if i + 1 < n and text[i + 1] == '"':
                            chars.append('"')  # escaped quote
                            i += 2
                        else:
                            i += 1  # closing quote
                            break
                    else:
                        chars.append(c)
                        i += 1
                # After a closing quote only a comma, newline or EOF
                # may follow.
                if i < n and text[i] not in ',\r\n':
                    raise ValueError(
                        "unexpected character after closing quote"
                    )
                record.append(''.join(chars))
            else:
                # Unquoted field: quotes have no special meaning here.
                start = i
                while i < n and text[i] not in ',\r\n':
                    i += 1
                record.append(text[start:i])

            # --- Decide what follows the field ---
            if i >= n:
                break  # EOF ends the record
            c = text[i]
            if c == ',':
                i += 1
                if i >= n:
                    # Trailing comma at EOF: one last empty field.
                    record.append('')
                    break
                continue  # parse the next field in this record
            # Newline ('\n' or '\r\n') ends the record.
            i += 1
            if c == '\r' and i < n and text[i] == '\n':
                i += 1
            break

        records.append(record)

    return records
