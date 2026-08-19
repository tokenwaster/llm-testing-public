from __future__ import annotations


def parse_csv(text: str) -> list[list[str]]:
    if text == "":
        return []

    n = len(text)

    def parse_field(i: int):
        if i >= n:
            return "", i, "eof"

        if text[i] == '"':
            i += 1
            parts = []

            while True:
                if i >= n:
                    raise ValueError("Unterminated quoted field")

                ch = text[i]

                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        parts.append('"')
                        i += 2
                        continue

                    i += 1

                    if i >= n:
                        return "".join(parts), i, "eof"

                    if text[i] == ",":
                        return "".join(parts), i + 1, "comma"

                    if text[i] == "\n":
                        return "".join(parts), i + 1, "newline"

                    if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
                        return "".join(parts), i + 2, "newline"

                    raise ValueError("Unexpected character after closing quote")

                parts.append(ch)
                i += 1

        parts = []

        while i < n:
            ch = text[i]

            if ch == ",":
                return "".join(parts), i + 1, "comma"

            if ch == "\n":
                return "".join(parts), i + 1, "newline"

            if ch == "\r" and i + 1 < n and text[i + 1] == "\n":
                return "".join(parts), i + 2, "newline"

            parts.append(ch)
            i += 1

        return "".join(parts), i, "eof"

    records = []
    i = 0

    while i < n:
        record = []

        while True:
            field, i, terminator = parse_field(i)
            record.append(field)

            if terminator == "comma":
                continue

            records.append(record)
            break

        if terminator == "eof":
            break

    return records
