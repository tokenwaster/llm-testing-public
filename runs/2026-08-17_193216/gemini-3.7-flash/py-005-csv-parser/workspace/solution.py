def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == '"':
            i += 1
            chars = []
            closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        chars.append('"')
                        i += 2
                    else:
                        closed = True
                        i += 1
                        break
                else:
                    chars.append(text[i])
                    i += 1

            if not closed:
                raise ValueError("Unclosed quote in CSV field")

            current_record.append("".join(chars))

            if i == n:
                records.append(current_record)
                break
            elif text[i] == ",":
                i += 1
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == "\n":
                i += 1
                records.append(current_record)
                current_record = []
                if i == n:
                    break
            elif text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                records.append(current_record)
                current_record = []
                if i == n:
                    break
            else:
                raise ValueError(
                    f"Unexpected character after closing quote: {text[i]!r}"
                )
        else:
            chars = []
            while i < n:
                c = text[i]
                if c == "," or c == "\n" or (c == "\r" and i + 1 < n and text[i + 1] == "\n"):
                    break
                chars.append(c)
                i += 1

            current_record.append("".join(chars))

            if i == n:
                records.append(current_record)
                break
            elif text[i] == ",":
                i += 1
                if i == n:
                    current_record.append("")
                    records.append(current_record)
                    break
            elif text[i] == "\n":
                i += 1
                records.append(current_record)
                current_record = []
                if i == n:
                    break
            elif text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                i += 2
                records.append(current_record)
                current_record = []
                if i == n:
                    break

    return records
