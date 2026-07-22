# solution.py

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data according to RFC‑4180 rules.
    Returns a list of records, each record being a list of fields.
    Raises ValueError for malformed input.
    """
    if text == "":
        return []

    rows = []
    i = 0
    n = len(text)

    def peek(offset=0):
        return text[i + offset] if i + offset < n else None

    while i < n:
        # start a new record
        row = []
        field = ""
        in_quotes = False
        quoted_field_started = False

        while True:
            ch = peek()
            if ch is None:  # EOF
                # end of last field and record
                if in_quotes:
                    raise ValueError("Unclosed quote at end of input")
                row.append(field)
                rows.append(row)
                i += 1  # move past EOF (no effect)
                break

            if not quoted_field_started:
                # handle unquoted field or start of quoted field
                if ch == '"':
                    in_quotes = True
                    quoted_field_started = True
                    i += 1
                    continue
                elif ch == ',':
                    row.append(field)
                    field = ""
                    i += 1
                    continue
                elif ch == '\r' or ch == '\n':
                    # end of record
                    if in_quotes:
                        raise ValueError("Unclosed quote before line break")
                    row.append(field)
                    rows.append(row)
                    # consume CRLF as one newline
                    if ch == '\r' and peek(1) == '\n':
                        i += 2
                    else:
                        i += 1
                    break
                else:
                    field += ch
                    i += 1
                    continue
            else:
                # inside quoted field
                if ch == '"':
                    next_ch = peek(1)
                    if next_ch == '"':  # escaped quote
                        field += '"'
                        i += 2
                        continue
                    else:  # closing quote
                        in_quotes = False
                        i += 1
                        # after closing quote, expect comma or newline or EOF
                        nxt = peek()
                        if nxt is None:
                            row.append(field)
                            rows.append(row)
                            break
                        elif nxt == ',':
                            row.append(field)
                            field = ""
                            i += 1
                            continue
                        elif nxt == '\r' or nxt == '\n':
                            if in_quotes:
                                raise ValueError("Unclosed quote before line break")
                            row.append(field)
                            rows.append(row)
                            if nxt == '\r' and peek(1) == '\n':
                                i += 2
                            else:
                                i += 1
                            break
                        else:
                            # any other character after closing quote is error
                            raise ValueError(f"Invalid character '{nxt}' after closing quote")
                else:
                    field += ch
                    i += 1
                    continue

    return rows
