def parse_csv(text: str) -> list[list[str]]:
    """
    Parses a CSV string according to RFC-4180 rules from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    
    in_quoted_field = False
    after_quote = False
    last_char_was_newline = False

    while i < n:
        char = text[i]

        if not in_quoted_field and not after_quote:
            # START or IN_UNQUOTED_FIELD
            if char == '"' and not current_field:
                in_quoted_field = True
                i += 1
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                i += 1
            elif char == '\n':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                last_char_was_newline = True
                i += 1
            elif char == '\r':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                last_char_was_newline = True
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                current_field.append(char)
                i += 1

        elif in_quoted_field:
            # IN_QUOTED_FIELD
            if char == '"':
                after_quote = True
                in_quoted_field = False
                i += 1
            else:
                current_field.append(char)
                i += 1

        elif after_quote:
            # AFTER_QUOTE_IN_QUOTED_FIELD (checking for escaped quote or field end)
            if char == '"':
                current_field.append('"')
                after_quote = False
                in_quoted_field = True
                i += 1
            elif char == ',':
                current_record.append("".join(current_field))
                current_field = []
                after_quote = False
                i += 1
            elif char == '\n':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                after_quote = False
                last_char_was_newline = True
                i += 1
            elif char == '\r':
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                after_quote = False
                last_char_was_newline = True
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
            else:
                raise ValueError("Invalid character after closing quote")

    if in_quoted_field:
        raise ValueError("Unclosed quote")

    # If the input did not end with a newline, we must process the final field and record.
    if not last_char_was_newline:
        current_record.append("".join(current_field))
        records.append(current_record)

    return records
