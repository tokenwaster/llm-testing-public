def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    # Normalize line endings to '\n' for easier processing while keeping
    # track of original content.
    text = text.replace("\r\n", "\n")

    records = []
    i = 0
    n = len(text)

    while i < n:
        # Read one record (up to '\n' or EOF)
        record = []
        field, i, closed = _parse_field(text, i)

        # After _parse_field, i points either at a comma, newline, or EOF.

        record.append(field)

        while i < n and text[i] == ",":
            i += 1  # consume comma
            field, i, closed = _parse_field(text, i)
            record.append(field)

        records.append(record)

        # After the last field of a record, expect newline or EOF
        if i < n and text[i] == "\n":
            i += 1  # consume newline
        elif i < n:
            # Malformed: characters after a closing quote that aren't comma/newline/EOF
            # _parse_field should have raised already if needed, but double-check
            raise ValueError(f"Malformed CSV: unexpected character {text[i]!r} after field at position {i}")

    # Trailing empty record from final newline should be removed
    # (handled by not appending after consuming newline above)

    return records


def _parse_field(text: str, i: int) -> tuple:
    """
    Parse one field starting at position i.
    Returns (field_value, new_position, quote_closed).
    """
    n = len(text)

    if i >= n:
        return ("", i, False)

    if text[i] != '"':
        # Unquoted field: read until comma, newline, or EOF
        start = i
        while i < n and text[i] not in (",", "\n"):
            i += 1
        return (text[start:i], i, False)

    # Quoted field
    i += 1  # consume opening quote
    start = i
    buf = []

    while i < n:
        if text[i] == '"':
            # Check if it's an escaped quote (doubled)
            if i + 1 < n and text[i + 1] == '"':
                buf.append('"')
                i += 2
            else:
                # Closing quote
                i += 1
                # After closing quote, next char must be comma, newline, or EOF
                buf.append(text[start:i - 1])  # placeholder, will be overwritten
                # Actually build string properly
                field = "".join(buf)
                # Re-extract since buf logic was flawed; redo:
                # We need to rebuild from start with escaping handled
                field = _decode_quoted(text, start, i)
                _check_after_quote(text, i)
                return (field, i, True)
        else:
            buf.append(text[i])
            i += 1

    # If we get here, the quote was never closed
    raise ValueError("Malformed CSV: unclosed quoted field")


def _decode_quoted(text: str, start: int, end: int) -> str:
    """
    Decode a quoted field: text[start:end] contains the content between
    opening and closing quotes (end points just after closing quote).
    Doubled quotes ("") decode to single quote.
    """
    # Re-parse from start to end-1 to handle escaped quotes
    result = []
    j = start
    while j < end - 1:  # end-1 because end points after closing quote
        if text[j] == '"':
            if j + 1 < end - 1 and text[j + 1] == '"':
                result.append('"')
                j += 2
            else:
                # A lone quote inside should not happen if parser is correct
                j += 1
        else:
            result.append(text[j])
            j += 1
    return "".join(result)


def _check_after_quote(text: str, i: int) -> None:
    """
    After a closing quote at position i-1, ensure next char is comma,
    newline, or EOF.
    """
    n = len(text)
    if i < n and text[i] not in (",", "\n"):
        raise ValueError(f'Malformed CSV: unexpected character {text[i]!r} after closing quote at position {i}')
