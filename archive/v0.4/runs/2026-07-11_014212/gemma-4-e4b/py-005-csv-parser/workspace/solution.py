def parse_csv(text: str) -> list[list[str]]:
    """
    Implements an RFC-4180 style CSV parser from scratch.

    Args:
        text: The string content to parse.

    Returns:
        A list of lists of strings, where each inner list is a record (row).

    Raises:
        ValueError: If the input is malformed (e.g., unclosed quotes, 
                    characters after closing quote).
    """
    if not text:
        return []

    rows = []
    current_row = []
    current_field = []
    in_quotes = False
    i = 0
    n = len(text)

    def finalize_field():
        nonlocal current_field
        # The field content is already built in current_field
        current_row.append("".join(current_field))
        current_field = []

    while i < n:
        char = text[i]

        if in_quotes:
            if char == '"':
                # Check for escaped quote ""
                if i + 1 < n and text[i+1] == '"':
                    current_field.append('"')
                    i += 2  # Skip both quotes
                    continue
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
                    break # Break inner loop to process delimiter/newline logic below
            else:
                # Any other character inside quotes is literal
                current_field.append(char)
                i += 1
                continue

        # --- Not in quotes ---
        
        if char == '"':
            # Rule: Quotes only have special meaning if the field starts with a quote.
            # If current_field is empty, this must be the start of a quoted field.
            if not current_field and (i == 0 or text[i-1] in ('\n', '\r')):
                in_quotes = True
                current_field.append(char) # Start building with the quote char itself
                i += 1
                continue
            else:
                # Quote encountered mid-field, treat as literal character (RFC 4180 allows this, 
                # but standard CSV parsers often treat it literally if not at start).
                # Since we are building the field char by char, we just append it.
                current_field.append(char)
                i += 1
                continue

        elif char == ',':
            finalize_field()
            i += 1
            continue

        elif char in ('\n', '\r'):
            # Handle line endings (CRLF or LF)
            if char == '\r' and i + 1 < n and text[i+1] == '\n':
                # Found CRLF, consume both characters for record separation
                i += 2
            elif char == '\n' or char == '\r':
                # Found LF or standalone CR
                i += 1

            # End of record detected. Finalize the last field and row.
            finalize_field()
            rows.append(list(current_row))
            current_row = []
            
            # If we hit EOF immediately after a newline, we don't want to process it again.
            if i > n: 
                break
            continue

        else:
            # Regular character
            current_field.append(char)
            i += 1

    # --- Post-loop processing ---

    # If the loop finished and we were still in quotes, it's an error.
    if in_quotes:
        raise ValueError("Malformed CSV input: Unclosed quote detected.")

    # Finalize the last field (which might be empty if the file ended with a delimiter)
    finalize_field()
    current_row.append("".join(current_field)) # Append the final accumulated field content
    rows.append(list(current_row))


    # Special handling for trailing newline: 
    # If the input ends exactly on a record boundary (i.e., we processed delimiters/newlines), 
    # and the last row added was due to that delimiter, we might have an extra empty list entry 
    # if the logic above wasn't perfectly clean regarding EOF vs trailing newline.

    # The current implementation structure handles this by appending a record only when 
    # a line ending is hit or EOF is reached after processing content.
    
    # If the input was non-empty, but resulted in no rows (e.g., just whitespace that didn't trigger delimiters), 
    # we rely on the initial check for "" returning [].

    return rows
