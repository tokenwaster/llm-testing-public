def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    while i < n:
        # Skip leading whitespace (though RFC-4180 doesn't specify, we'll assume none)
        if text[i] == ' ' or text[i] == '\t':
            i += 1
            continue

        # Handle record separator
        if text[i] in ('\n', '\r'):
            if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                i += 2
            else:
                i += 1
            records.append(current_record)
            current_record = []
            continue

        # Start of a new field
        j = i
        in_quotes = False
        if text[j] == '"':
            in_quotes = True
            j += 1

        field_start = j
        while j < n:
            if in_quotes:
                if text[j] == '"':
                    # Check for doubled quote
                    if j + 1 < n and text[j+1] == '"':
                        j += 2
                        continue
                    else:
                        # End of quoted field
                        in_quotes = False
                        j += 1
                        break
                j += 1
            else:
                if text[j] == ',':
                    j += 1
                    break
                elif text[j] in ('\n', '\r'):
                    if text[j] == '\r' and j + 1 < n and text[j+1] == '\n':
                        j += 2
                    else:
                        j += 1
                    break
                j += 1

        # Check for malformed input
        if in_quotes:
            raise ValueError("Unclosed quote")

        # Extract the field content
        field_content = text[field_start:j]
        # Remove surrounding quotes and handle escaped quotes inside
        if in_quotes or (text[i] == '"' and j > i + 1 and text[j-1] == '"'):
            # This shouldn't happen because we checked in_quotes above, but just in case
            pass

        # Process the field content to handle doubled quotes
        processed_field = []
        k = 0
        m = len(field_content)
        while k < m:
            if field_content[k] == '"' and k + 1 < m and field_content[k+1] == '"':
                processed_field.append('"')
                k += 2
            else:
                processed_field.append(field_content[k])
                k += 1

        current_record.append(''.join(processed_field))

        # Check for malformed input after closing quote
        if j < n and text[j-1] == '"' and text[j] not in (',', '\n', '\r'):
            raise ValueError("Characters after closing quote")

        i = j

    # Add the last record if there's any content left
    if current_record:
        records.append(current_record)

    return records
