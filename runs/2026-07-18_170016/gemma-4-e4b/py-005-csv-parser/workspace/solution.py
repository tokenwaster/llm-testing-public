def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.

    Args:
        text: The input CSV content string.

    Returns:
        A list of lists of strings, where each inner list is a record (row).

    Raises:
        ValueError: If the input is malformed (e.g., unclosed quotes, 
                    or characters after closing quote that aren't delimiters/EOF).
    """
    if not text:
        return []

    results = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        # --- Handle Line Endings (Record Separators) ---
        is_eol = char == '\r' or char == '\n'
        if is_eol and not in_quotes:
            # A record boundary is hit, but only if we are NOT inside quotes.
            
            # 1. Finalize the current field/record based on the characters processed so far.
            current_record.append(current_field)
            results.append(current_record[:]) # Append a copy of the record
            
            # Reset for the next record
            current_record = []
            current_field = ""

            # 2. Skip all subsequent line break characters (CRLF or LF)
            if char == '\r':
                i += 1
                if i < n and text[i] == '\n':
                    i += 1 # Consumed \r\n
                else:
                    i += 1 # Consumed standalone \r
            elif char == '\n':
                i += 1
            continue

        # --- Handle Quotes ---
        if char == '"':
            if in_quotes:
                # Check for escaped quote ""
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 2 # Skip both quotes
                    continue
                else:
                    # Closing quote found. We must check what follows immediately.
                    i += 1
                    next_char = None
                    if i < n:
                        next_char = text[i]

                    # If the closing quote is followed by anything other than a comma or EOL, it's an error.
                    if next_char not in (',', '\r', '\n'):
                        raise ValueError(f"Malformed CSV input: characters found after closing quote at index {i-1}.")

                    in_quotes = False
                    # Do NOT append the quote itself; it was structural. 
                    # The loop will continue processing the delimiter/next char normally.
                    continue
            else:
                # Starting a quoted field
                in_quotes = True
                # We do not append the opening quote to current_field
                i += 1
                continue

        # --- Handle Commas (Field Separators) ---
        elif char == ',':
            if in_quotes:
                current_field += ','
                i += 1
                continue
            else:
                # Field ends. Finalize the field and start a new one.
                current_record.append(current_field)
                current_field = ""
                i += 1
                continue

        # --- Handle Regular Characters ---
        else:
            if in_quotes:
                current_field += char
            else:
                current_field += char
            i += 1

    # --- Post-Loop Processing and Error Checking ---

    # 1. Check for unclosed quotes at EOF
    if in_quotes:
        raise ValueError("Malformed CSV input: opening quote was never closed.")

    # 2. Finalize the last field/record if content was processed
    if current_field or (not results and not current_record):
        current_record.append(current_field)
        results.append(current_record[:])

    # Handle the specific case where input is just empty lines, resulting in [] initially 
    # but needing to return [[], [], ...] if multiple records were processed.
    if not results and current_record:
         return [current_record]
    elif not results and text == "":
        return []

    return results
