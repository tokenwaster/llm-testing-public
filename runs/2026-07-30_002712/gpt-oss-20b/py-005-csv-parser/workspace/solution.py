# solution.py

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data according to RFC‑4180 rules.
    Raises ValueError for malformed input.
    """
    if text == "":
        return []

    rows = []
    cur_row = []
    cur_field = []
    i = 0
    n = len(text)

    # Helper: consume a newline sequence and return the consumed length
    def consume_newline(idx):
        if idx < n and text[idx] == "\r":
            if idx + 1 < n and text[idx + 1] == "\n":
                return 2
            else:
                return 1
        elif idx < n and text[idx] == "\n":
            return 1
        return 0

    while i < n:
        ch = text[i]
        if not cur_field:  # start of a field
            if ch == '"':
                # quoted field
                i += 1
                while True:
                    if i >= n:
                        raise ValueError("Unclosed quote")
                    c = text[i]
                    if c == '"':
                        # could be end or escaped quote
                        if i + 1 < n and text[i + 1] == '"':
                            cur_field.append('"')
                            i += 2
                        else:
                            i += 1
                            break  # end of quoted field
                    else:
                        cur_field.append(c)
                        i += 1
                # after closing quote, next must be comma or newline or EOF
                if i < n:
                    nxt = text[i]
                    if nxt == ',':
                        cur_row.append(''.join(cur_field))
                        cur_field = []
                        i += 1
                        continue
                    elif nxt in ("\n", "\r"):
                        # finish record
                        cur_row.append(''.join(cur_field))
                        cur_field = []
                        rows.append(cur_row)
                        cur_row = []
                        nl_len = consume_newline(i)
                        i += nl_len
                        continue
                    else:
                        raise ValueError(f"Invalid character after closing quote: {nxt!r}")
                else:
                    # EOF after quoted field
                    cur_row.append(''.join(cur_field))
                    cur_field = []
                    rows.append(cur_row)
                    cur_row = []
                    break
            elif ch == ',':
                # empty field
                cur_row.append('')
                i += 1
            elif ch in ("\n", "\r"):
                # empty field at end of line
                cur_row.append('')
                rows.append(cur_row)
                cur_row = []
                nl_len = consume_newline(i)
                i += nl_len
            else:
                # unquoted field start
                cur_field.append(ch)
                i += 1
        else:
            # inside an unquoted field (no starting quote)
            if ch == ',':
                cur_row.append(''.join(cur_field))
                cur_field = []
                i += 1
            elif ch in ("\n", "\r"):
                cur_row.append(''.join(cur_field))
                rows.append(cur_row)
                cur_row = []
                nl_len = consume_newline(i)
                i += nl_len
            else:
                cur_field.append(ch)
                i += 1

    # After loop, if we ended inside a field (unclosed quote), error
    if cur_field or cur_row:
        # If we ended with an empty field at the very end without newline,
        # it should be added.
        if cur_field:
            cur_row.append(''.join(cur_field))
        rows.append(cur_row)

    return rows
