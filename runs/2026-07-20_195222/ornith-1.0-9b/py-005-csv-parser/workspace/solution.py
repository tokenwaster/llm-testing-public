def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    pos = 0
    n = len(text)

    while pos < n:
        row = []

        while True:
            # Try to parse a field
            if pos >= n:
                break

            field, new_pos = _parse_field(text, pos, n)

            if field is None:
                break

            row.append(field)
            pos = new_pos

            # Check what follows this field
            if pos >= n:
                break  # End of record (no more fields after this one)

            ch = text[pos]
            if ch == ',':
                pos += 1
                # Trailing comma means an additional empty field at end of record
                if pos >= n:
                    row.append('')
                    break
                continue  # Parse next field
            elif ch in ('\r', '\n'):
                # Handle CRLF together; lone \r is also a separator
                if ch == '\r' and pos + 1 < n and text[pos + 1] == '\n':
                    pos += 2
                else:
                    pos += 1
                break  # End of record (line ending)
            else:
                raise ValueError(f"Unexpected character after field: {ch!r}")

        records.append(row)

    return records


def _parse_field(text, pos, n):
    """Parse a single CSV field starting at position `pos`.

    Returns (field_value, new_pos) where new_pos is the position after the field.
    Raises ValueError for malformed input.
    """
    ch = text[pos]

    if ch == '"':
        # Quoted field
        pos += 1
        result = []
        while pos < n:
            c = text[pos]
            if c == '"':
                if pos + 1 < n and text[pos + 1] == '"':
                    # Escaped quote — decode to single "
                    result.append('"')
                    pos += 2
                else:
                    # End of quoted field — advance past closing quote
                    pos += 1
                    return (''.join(result), pos)
            elif c in ('\r', '\n'):
                # Newline inside quoted field is literal content
                result.append(c)
                pos += 1
            else:
                result.append(c)
                pos += 1

        raise ValueError("Unclosed quote")
    else:
        # Unquoted field — read until comma, newline, or end of input
        result = []
        while pos < n and text[pos] not in (',', '\r', '\n'):
            result.append(text[pos])
            pos += 1
        return (''.join(result), pos)
