def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == '"':
            # Quoted field
            i += 1  # Skip opening quote
            val = []
            quote_closed = False
            while i < n:
                if text[i] == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        val.append('"')
                        i += 2
                    else:
                        rem = text[i + 1 :]
                        if (
                            not rem
                            or rem.startswith(",")
                            or rem.startswith("\n")
                            or rem.startswith("\r\n")
                        ):
                            quote_closed = True
                            i += 1  # Skip closing quote
                            break
                        else:
                            raise ValueError(
                                "Invalid character after closing quote"
                            )
                else:
                    val.append(text[i])
                    i += 1

            if not quote_closed:
                raise ValueError("Unclosed quoted field")

            field_val = "".join(val)
        else:
            # Unquoted field
            val = []
            while i < n:
                if (
                    text[i] == ","
                    or text[i] == "\n"
                    or text[i : i + 2] == "\r\n"
                ):
                    break
                val.append(text[i])
                i += 1
            field_val = "".join(val)

        current_record.append(field_val)

        if i == n:
            records.append(current_record)
            current_record = []
            break
        elif text[i] == ",":
            i += 1
            if i == n:
                current_record.append("")
                records.append(current_record)
                current_record = []
                break
        elif text[i : i + 2] == "\r\n":
            i += 2
            records.append(current_record)
            current_record = []
        elif text[i] == "\n":
            i += 1
            records.append(current_record)
            current_record = []

    return records
