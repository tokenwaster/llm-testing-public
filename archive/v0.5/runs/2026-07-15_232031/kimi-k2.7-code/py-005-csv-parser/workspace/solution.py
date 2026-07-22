def parse_csv(text: str) -> list[list[str]]:
    records: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)

    def flush_field() -> None:
        row.append("".join(field))
        field.clear()

    def flush_row() -> None:
        nonlocal row
        records.append(row)
        row = []

    def is_crlf_at(pos: int) -> bool:
        return pos + 1 < n and text[pos] == "\r" and text[pos + 1] == "\n"

    while i < n:
        ch = text[i]

        if ch == '"':
            # Quoted field
            i += 1
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field.append('"')
                        i += 2
                    else:
                        closed = True
                        i += 1
                        break
                else:
                    field.append(text[i])
                    i += 1

            if not closed:
                raise ValueError("unterminated quoted field")

            if i < n:
                nxt = text[i]
                if nxt == ",":
                    flush_field()
                    i += 1
                elif nxt == "\n":
                    flush_field()
                    flush_row()
                    i += 1
                elif is_crlf_at(i):
                    flush_field()
                    flush_row()
                    i += 2
                else:
                    raise ValueError("invalid character after closing quote")
            else:
                flush_field()

        elif ch == ",":
            flush_field()
            i += 1

        elif ch == "\n":
            flush_field()
            flush_row()
            i += 1

        elif is_crlf_at(i):
            flush_field()
            flush_row()
            i += 2

        else:
            # Unquoted field: read until comma, \n, or \r\n
            while i < n:
                c = text[i]
                if c == "," or c == "\n":
                    break
                if c == "\r" and i + 1 < n and text[i + 1] == "\n":
                    break
                field.append(c)
                i += 1
            # Delimiter is handled by the next iteration.

    if field:
        row.append("".join(field))
    if row or (not records and n > 0):
        records.append(row)

    return records
