def parse_csv(text: str) -> list[list[str]]:
    """Parse RFC-4180-style CSV text into a list of rows (each a list of fields)."""
    records: list[list[str]] = []
    current_record: list[str] = []
    field_chars: list[str] = []
    in_quotes = False          # currently inside a quoted section
    quoted_field = False       # current field began with a quote (not yet reset)
    has_pending = False        # an unfinished record exists awaiting finalization

    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i + 1] == '"':
                    field_chars.append('"')   # escaped quote -> one "
                    i += 2
                    continue
                in_quotes = False             # closing quote
                i += 1
                continue
            field_chars.append(c)
            i += 1
            continue

        # Not inside quotes.
        if c == '"':
            if not field_chars:
                in_quotes = True
                quoted_field = True
                has_pending = True
                i += 1
                continue
            field_chars.append(c)             # literal quote mid-field
            has_pending = True
            i += 1
            continue

        if c == ',':
            current_record.append(''.join(field_chars))
            field_chars = []
            quoted_field = False
            i += 1
            continue

        if c == '\r':
            if i + 1 < n and text[i + 1] == '\n':
                i += 2
            else:
                i += 1
            current_record.append(''.join(field_chars))
            field_chars = []
            quoted_field = False
            has_pending = False
            records.append(current_record)
            current_record = []
            continue

        if c == '\n':
            current_record.append(''.join(field_chars))
            field_chars = []
            quoted_field = False
            has_pending = False
            records.append(current_record)
            current_record = []
            i += 1
            continue

        # Ordinary character.
        if quoted_field:
            raise ValueError("unexpected characters after closing quote")
        field_chars.append(c)
        has_pending = True
        i += 1

    if in_quotes:
        raise ValueError("unterminated quoted field")

    if has_pending:
        current_record.append(''.join(field_chars))
        records.append(current_record)

    return records
