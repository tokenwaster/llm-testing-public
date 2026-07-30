import re

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.

    Args:
        text: The input CSV data string.

    Returns:
        A list of lists of strings, where each inner list is a record (row).

    Raises:
        ValueError: If the input is malformed (e.g., unclosed quotes, 
                    invalid characters after closing quote).
    """
    if not text:
        return []

    results = []
    current_record = []
    field_buffer = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        # --- State: Reading a Field (Not in quotes) ---
        if field_buffer and not current_in_quotes:
            if char == ',':
                field_buffer.append("".join(field_buffer))
                field_buffer = []
                i += 1
                continue

            elif char == '\n' or (char == '\r' and i + 1 < n and text[i+1] == '\n'):
                # End of record detected.
                if field_buffer:
                    field_buffer.append("".join(field_buffer))
                    field_buffer = []
                current_record.append(field_buffer)
                results.append(list(current_record))
                current_record = []
                field_buffer = []
                i += 1
                # Skip the \r if we consumed it as part of \r\n
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                continue

            elif char == '"':
                # Start of a quoted field
                current_in_quotes = True
                field_buffer.append(char)
                i += 1
                continue
            
            else:
                # Regular character
                field_buffer.append(char)
                i += 1
                continue

        # --- State: Initializing/Starting a Field (Empty field or start of line) ---
        if not field_buffer and not current_record:
             # This handles the very first characters, or fields after a newline
            pass # Fall through to general logic below

        # --- Handling Newlines at Start of Field ---
        if char == '\n' or (char == '\r' and i + 1 < n and text[i+1] == '\n'):
            # This handles the case where a field is empty due to consecutive delimiters/newlines.
            # If we are starting a new record, we must append an empty field.
            if not current_record: # Only process if we haven't started collecting fields for this line yet
                field_buffer.append("")
                current_record.append(field_buffer)
                results.append(list(current_record))
                current_record = []
                field_buffer = []
            i += 1
            if char == '\r' and i + 1 < n and text[i+1] == '\n':
                i += 1 # Skip the \n after \r\n
            continue

        # --- State: Inside Quotes (Handling escaped quotes) ---
        if current_in_quotes:
            if char == '"':
                # Check for "" escape sequence
                if i + 1 < n and text[i+1] == '"':
                    field_buffer.append('"') # Decode "" to "
                    i += 2
                    continue
                else:
                    # Closing quote detected
                    current_in_quotes = False
                    field_buffer.append(char)
                    
                    # Check what follows the closing quote
                    next_char_index = i + 1
                    if next_char_index < n:
                        next_char = text[next_char_index]
                        if next_char not in (',', '\n', '\r'):
                            raise ValueError(f"Malformed CSV: Characters found after closing quote at index {i+1}: '{text[next_char_index:]}'")
                    
                    # If we are here, the field is closed. We must check if it's followed by a delimiter or EOF.
                    if next_char_index < n and text[next_char_index] == ',':
                        i += 1 # Consume comma
                        field_buffer.append("") # Placeholder for the empty field after the quote, handled below
                        current_record.append(list(field_buffer))
                        field_buffer = []
                    elif next_char_index < n and (text[next_char_index] == '\n' or text[next_char_index] == '\r'):
                         # Newline handled by the main loop logic after index update
                         pass 
                    else:
                        # If it ends here, we just finished a field.
                        current_record.append(list(field_buffer))
                        field_buffer = []

                    i += 1 # Consume the closing quote
                    continue
            else:
                # Regular character inside quotes
                field_buffer.append(char)
                i += 1
                continue

        # --- State: Normal Character (Not in quotes, not a delimiter/newline) ---
        if char != ',' and char != '\n' and char != '\r':
            field_buffer.append(char)
            i += 1
            continue

        # If we reach here without consuming the character, it means it was an unhandled state transition or error.
        # This should ideally not happen if logic is perfect, but serves as a safeguard.
        if i < n:
             i += 1


    # --- Post-processing and Finalization ---

    # If we finished processing the text and there are fields accumulated in field_buffer, 
    # it means the last record was not terminated by a newline.
    if field_buffer or current_record:
        current_record.append(list(field_buffer))
        results.append(list(current_record))

    # Handle trailing empty lines (which should only happen if the input ended with \n)
    # The logic above handles this implicitly by how records are appended upon newline detection.
    
    return results
