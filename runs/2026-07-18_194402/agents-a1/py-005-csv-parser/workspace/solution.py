def parse_csv(text: str) -> list[list[str]]:
    records = []
    current_record = []  # fields for the current line
    current_field = []   # characters for the current field being built
    in_quotes = False
    after_quote = False
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        if in_quotes:
            if c == '"':
                if i + 1 < n and text[i+1] == '"':
                    # Escaped quote inside quoted field
                    current_field.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote of the field
                    in_quotes = False
                    after_quote = True
                    i += 1
                    continue
            elif c == '\r':
                if i + 1 < n and text[i+1] == '\n':
                    current_field.append('\r')
                    current_field.append('\n')
                    i += 2
                    continue
                else:
                    current_field.append(c)
                    i += 1
                    continue
            elif c == '\n':
                current_field.append(c)
                i += 1
                continue
            else:
                current_field.append(c)
                i += 1
                continue
        else:
            if after_quote:
                # After a closing quote, only comma, newline, or \r\n allowed
                if c == ',' or c == '\n':
                    after_quote = False
                    # Let the separator be processed in normal flow
                    continue
                elif c == '\r' and i + 1 < n and text[i+1] == '\n':
                    after_quote = False
                    continue
                else:
                    raise ValueError("Invalid character after closing quote")
            else:
                # Normal processing outside quotes
                if c == '"':
                    if not current_field:  # start quoted field
                        in_quotes = True
                        i += 1
                        continue
                    else:
                        current_field.append(c)
                        i += 1
                        continue
                elif c == ',':
                    # End of current field
                    current_record.append(''.join(current_field))
                    current_field = []
                    i += 1
                    continue
                elif c == '\r':
                    if i + 1 < n and text[i+1] == '\n':
                        # End of record (\r\n)
                        current_record.append(''.join(current_field))
                        records.append(current_record)
                        current_record = []
                        current_field = []
                        i += 2
                        continue
                    else:
                        current_field.append(c)
                        i += 1
                        continue
                elif c == '\n':
                    # End of record (\n)
                    current_record.append(''.join(current_field))
                    records.append(current_record)
                    current_record = []
                    current_field = []
                    i += 1
                    continue
                else:
                    current_field.append(c)
                    i += 1
                    continue

    # Check for unclosed quoted field
    if in_quotes:
        raise ValueError("Unclosed quoted field")

    # Finalize any pending field and record
    if current_record or after_quote or current_field:
        current_record.append(''.join(current_field))
        records.append(current_record)

    return records
