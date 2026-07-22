# solution.py

def parse_csv(text: str) -> list[list[str]]:
    """
    Parse a string containing CSV data according to RFC‑4180 rules.
    Raises ValueError on malformed input.
    """
    if text == "":
        return []

    rows = []
    i = 0
    n = len(text)

    while i < n:
        fields: list[str] = []
        field_chars: list[str] = []
        quoted = False

        # Process a single record until newline or EOF
        while True:
            if i >= n:
                # End of file reached; finalize last field and row
                break

            ch = text[i]

            # Handle CRLF as a single line terminator
            if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                break  # end of record
            elif ch == "\n":
                i += 1
                break  # end of record

            if quoted:
                if ch == '"':
                    # Possible closing quote or escaped double quote
                    if i + 1 < n and text[i + 1] == '"':
                        field_chars.append('"')
                        i += 2
                        continue
                    else:
                        # Closing quote
                        quoted = False
                        i += 1
                        # After a closing quote, next char must be comma or line break/EOF
                        if i < n and text[i] not in {',', '\n'}:
                            if text[i] == '\r' and i + 1 < n and text[i + 1] == '\n':
                                pass  # handled below
                            else:
                                raise ValueError(f"Invalid character after closing quote at position {i}")
                        continue
                else:
                    field_chars.append(ch)
                    i += 1
                    continue

            # Not quoted
            if ch == ',':
                fields.append("".join(field_chars))
                field_chars = []
                i += 1
                continue
            elif ch == '"':
                if not field_chars:  # quote at start of field
                    quoted = True
                    i += 1
                    continue
                else:
                    # Quote inside unquoted field is literal
                    field_chars.append('"')
                    i += 1
                    continue
            else:
                field_chars.append(ch)
                i += 1

        # End of record reached (either by newline or EOF)
        fields.append("".join(field_chars))

        # If we ended due to a line break, add the row.
        # For trailing newline at end of input, we should not add an empty row.
        if i < n or (i == n and text.endswith(("\n", "\r\n"))):
            rows.append(fields)
        else:
            # EOF without newline: still need to append last record
            rows.append(fields)

    return rows
