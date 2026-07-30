def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    def parse_field(text: str, i: int) -> tuple[str, int]:
        N = len(text)
        if i < N and text[i] == '"':
            val = []
            idx = i + 1
            while idx < N:
                if text[idx] == '"':
                    if idx + 1 < N and text[idx + 1] == '"':
                        val.append('"')
                        idx += 2
                    else:
                        # Closing quote
                        idx += 1
                        if idx == N:
                            return "".join(val), idx
                        elif text[idx] == ',':
                            return "".join(val), idx
                        elif text[idx] == '\n':
                            return "".join(val), idx
                        elif text[idx] == '\r' and idx + 1 < N and text[idx + 1] == '\n':
                            return "".join(val), idx
                        else:
                            raise ValueError("Malformed CSV: invalid character after closing quote")
                else:
                    val.append(text[idx])
                    idx += 1
            raise ValueError("Malformed CSV: unclosed quote")
        else:
            val = []
            idx = i
            while idx < N:
                if text[idx] == ',':
                    break
                elif text[idx] == '\n':
                    break
                elif text[idx] == '\r' and idx + 1 < N and text[idx + 1] == '\n':
                    break
                else:
                    val.append(text[idx])
                    idx += 1
            return "".join(val), idx

    records = []
    current_row = []
    i = 0
    N = len(text)

    while i < N:
        val, next_i = parse_field(text, i)
        current_row.append(val)
        
        if next_i == N:
            records.append(current_row)
            current_row = []
            i = N
        elif text[next_i] == ',':
            i = next_i + 1
            if i == N:
                current_row.append("")
                records.append(current_row)
        elif text[next_i] == '\n':
            records.append(current_row)
            current_row = []
            i = next_i + 1
        elif text[next_i] == '\r':
            records.append(current_row)
            current_row = []
            i = next_i + 2

    return records
