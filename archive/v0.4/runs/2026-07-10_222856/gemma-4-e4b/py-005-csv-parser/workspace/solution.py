def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.

    Args:
        text: The input CSV content string.

    Returns:
        A list of lists of strings, representing the parsed records.

    Raises:
        ValueError: If the input is malformed (e.g., unclosed quotes, 
                    or characters after a closing quote that aren't delimiters).
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    i = 0
    n = len(text)
    in_quotes = False

    while i < n:
        char = text[i]

        # --- Handle Line Endings (Record Separators) ---
        if char == '\r' and i + 1 < n and text[i+1] == '\n':
            # Found CRLF (\r\n). This ends the current record.
            record_end = True
            i += 2  # Skip both \r and \n
        elif char == '\n':
            # Found LF (\n). This ends the current record.
            record_end = True
            i += 1
        else:
            record_end = False

        if record_end:
            # Finalize the current field (which might be empty if we hit a newline immediately)
            current_record.append("".join(current_field))
            current_field = []
            records.append(list(current_record))
            current_record = []
            continue # Restart loop iteration after skipping the line break

        # --- Handle Quoted Fields ---
        if char == '"':
            # Check if this quote starts a field (i.e., current_field is empty)
            is_start_quote = not current_field and not current_record and i > 0 and text[i-1] in ('\r', '\n', ',')

            if is_start_quote:
                in_quotes = True
                current_field.append(char) # Keep the quote for now, we process it below
                i += 1
                continue

            elif in_quotes:
                # Check for escaped double quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"') # Decode "" to "
                    i += 2
                    continue
                else:
                    # Closing quote or literal quote inside a field (which is fine)
                    in_quotes = False
                    current_field.append(char)
                    i += 1
                    continue

            elif not in_quotes and current_field:
                # Quote encountered mid-field, but it didn't start the field. Treat as literal text.
                current_field.append(char)
                i += 1
                continue

        # --- Handle Delimiters (Comma) ---
        elif char == ',':
            if in_quotes:
                # Comma inside quotes is literal data
                current_field.append(char)
                i += 1
                continue
            else:
                # Field separator found. Finalize the current field.
                current_record.append("".join(current_field))
                current_field = []
                i += 1
                continue

        # --- Handle Normal Characters (Data) ---
        else:
            if in_quotes:
                # Inside quotes, append character literally
                current_field.append(char)
                i += 1
            elif current_field or current_record:
                # Outside quotes, appending data
                current_field.append(char)
                i += 1
            else:
                # This handles the very first character of the input text
                current_field.append(char)
                i += 1

    # --- Post-Processing and Finalization ---

    # If we finished processing, finalize the last field/record if data was accumulated
    if current_field or current_record:
        current_record.append("".join(current_field))
        records.append(list(current_record))

    # Check for unclosed quotes at EOF
    if in_quotes:
        raise ValueError("Unclosed quote detected.")

    # Handle the case where the input ended with a trailing newline (which was processed 
    # by the record_end logic, but we must ensure we don't add an extra empty record).
    # The structure above handles this correctly because if the last character 
    # triggered 'record_end', it already finalized the record.

    return records
