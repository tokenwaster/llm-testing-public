def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    post_quote = False
    at_start_of_field = True
    last_char_was_newline = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]
        # Track if the current character is a newline to handle trailing newline rule.
        last_char_was_newline = (char == '\n' or char == '\r')

        if in_quotes:
            if char == '"':
                # Check for escaped double-quote ("")
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 1  # Skip the second quote
                else:
                    # End of quoted field
                    in_quotes = False
                    post_quote = True
            else:
                current_field += char
        elif post_quote:
            if char == ',':
                current_record.append(current_field)
                current_field = ""
                at_start_of_field = True
                post_quote = False
            elif char == '\n' or char == '\r':
                # End of record
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
                at_start_of_field = True
                post_quote = False
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
            else:
                # Characters after a closing quote that aren't comma/newline/EOF are invalid.
                raise ValueError("Characters after closing quote")
        else:  # Not in quotes, not post-quote (unquoted field mode)
            if at_start_of_field:
                if char == '"':
                    in_quotes = True
                    current_field = ""
                    at_start_of_field = False
                elif char == ',':
                    # Empty field between commas or after a comma/newline.
                    current_record.append("")
                    at_start_of_field = True
                elif char == '\n' or char == '\r':
                    # End of record, and the current field was empty.
                    current_record.append("")
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    at_start_of_field = True
                    if char == '\r' and i + 1 < n and text[i+1] == '\n':
                        i += 1
                else:
                    # Start of a new unquoted field.
                    current_field += char
                    at_start_of_field = False
            else:  # In the middle of an unquoted field
                if char == ',':
                    current_record.append(current_field)
                    current_field = ""
                    at_start_of_field = True
                elif char == '\n' or char == '\r':
                    # End of record.
                    current_record.append(current_field)
                    records.append(current_record)
                    current_record = []
                    current_field = ""
                    at_start_of_field = True
                    if char == '\r' and i + 1 < n and text[i+1] == '\n':
                        i += 1
                elif char == '"':
                    # Quotes are only special if they start a field.
                    raise ValueError("Unexpected quote in unquoted field")
                else:
                    current_field += char
        i += 1

    # Check for malformed input (unclosed quotes).
    if in_quotes:
        raise ValueError("Unclosed quote")

    # Finalize the last record/field if we didn't end on a newline.
    # If text ends with a comma, it implies an empty field follows.
    # If text ends without a newline, we must add the current field to the record.
    if not last_char_was_newline:
        if not at_start_of_field:
            current_record.append(current_field)
        else:
            current_record.append("")
        records.append(current_record)

    return records
