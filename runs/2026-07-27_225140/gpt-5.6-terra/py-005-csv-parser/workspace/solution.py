def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    rows: list[list[str]] = []
    row: list[str] = []
    field: list[str] = []
    i = 0
    n = len(text)
    ended_with_record_separator = False

    while i < n:
        ch = text[i]

        # Quoting is special only at the beginning of a field.
        if ch == '"' and not field:
            i += 1
            quoted: list[str] = []

            while i < n:
                ch = text[i]

                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        quoted.append('"')
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    quoted.append(ch)
                    i += 1
            else:
                raise ValueError("unterminated quoted field")

            field.extend(quoted)

            if i == n:
                ended_with_record_separator = False
                continue

            if text[i] == ",":
                row.append("".join(field))
                field = []
                i += 1
                ended_with_record_separator = False
                continue

            if text[i] == "\n":
                row.append("".join(field))
                rows.append(row)
                row = []
                field = []
                i += 1
                ended_with_record_separator = True
                continue

            if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                row.append("".join(field))
                rows.append(row)
                row = []
                field = []
                i += 2
                ended_with_record_separator = True
                continue

            raise ValueError("characters after closing quote")

        if ch == ",":
            row.append("".join(field))
            field = []
            i += 1
            ended_with_record_separator = False
        elif ch == "\n":
            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
            i += 1
            ended_with_record_separator = True
        elif ch == "\r" and i + 1 < n and text[i + 1] == "\n":
            row.append("".join(field))
            rows.append(row)
            row = []
            field = []
            i += 2
            ended_with_record_separator = True
        else:
            field.append(ch)
            i += 1
            ended_with_record_separator = False

    if not ended_with_record_separator:
        row.append("".join(field))
        rows.append(row)

    return rows
