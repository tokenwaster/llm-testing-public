import re

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses CSV text according to RFC-4180 rules from scratch.
    Handles quoted fields, escaped quotes (""), commas, and various line endings.
    """
    if not text:
        return []

    records = []
    current_record = []
    field_buffer = []
    i = 0
    n = len(text)

    # State variables
    in_quotes = False
    start_of_field = True # Tracks if the current field is starting (useful for initial quote check)

    while i < n:
        char = text[i]

        if in_quotes:
            # --- STATE: INSIDE QUOTES ---
            if char == '"':
                # Check for escaped double quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    field_buffer.append('"')
                    i += 2  # Consume both quotes
                    start_of_field = False
                    continue
                else:
                    # Closing quote encountered
                    in_quotes = False
                    i += 1
                    
                    # Check for malformed input immediately after closing quote
                    # The next character must be a comma, newline, or EOF.
                    j = i
                    while j < n and text[j] not in (',', '\n', '\r'):
                        if text[j].strip(): # If we find any non-whitespace char that isn't separator
                            raise ValueError(f"Malformed CSV: Characters found after closing quote at index {i}: '{text[j:]}'")
                        j += 1
                    
                    # Advance i past potential trailing whitespace/separators handled by the loop structure below
                    # We let the main logic handle the transition (comma/newline)
                    continue

            else:
                # Any other character inside quotes is literal
                field_buffer.append(char)
                i += 1
                start_of_field = False
        
        else:
            # --- STATE: OUTSIDE QUOTES ---
            if char == '"':
                # Quotes only have special meaning if the field starts with a quote
                if start_of_field and not field_buffer:
                    in_quotes = True
                    i += 1
                    start_of_field = False # We are now processing content, so it's no longer "starting"
                    continue
                else:
                    # Quote found mid-field (e.g., a"b). This is treated as literal text.
                    field_buffer.append(char)
                    i += 1
                    start_of_field = False

            elif char == ',':
                # Field separator found
                record_fields = "".join(field_buffer)
                current_record.append(record_fields)
                field_buffer = []
                start_of_field = True
                i += 1

            elif char == '\n' or char == '\r':
                # Line ending detected (must be outside quotes)
                
                # Handle CRLF (\r\n) sequence
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    line_end = True # Signal that we consumed both chars
                    i += 2
                else:
                    line_end = True
                    i += 1

                # Process the completed record (even if empty)
                records.append(current_record[:])
                current_record[:] = []
                field_buffer = []
                start_of_field = True
                continue # Continue loop after processing line end

            else:
                # Regular character
                field_buffer.append(char)
                i += 1
                start_of_field = False

    # --- POST-PROCESSING ---

    # 1. Handle the last field/record if we reached EOF without a final newline
    if i == n:
        # If there's content buffered, it must be the last field of the current record.
        if field_buffer or (not records and not current_record):
            current_record.append("".join(field_buffer))

    # 2. Finalize the last record if one was started but never terminated by a newline
    # This handles inputs like "a,b" (no trailing \n)
    if field_buffer or current_record:
        records.append(current_record[:])
        current_record[:] = []

    return records


# Example usage and testing structure (not part of the final output block):
# print(parse_csv("")) # Expected: []
# print(parse_csv("a,b")) # Expected: [['a', 'b']]
# print(parse_csv("a,,b")) # Expected: [['a', '', 'b']]
# print(parse_csv('a\nb')) # Expected: [['a'], ['b']]
# print(parse_csv('a\r\n b')) # Expected: [['a'], [' b']] (assuming standard CSV behavior where whitespace is preserved)

# Quoted fields test
# print(parse_csv('"a,b"\nc')) # Expected: [['a,b', 'c']]
# print(parse_csv('"a""b",c')) # Expected: [['a"b', 'c']]
# print(parse_csv('a,"line\nbreak",c')) # Expected: [['a', 'line\nbreak', 'c']]

# Edge case test (Trailing newline)
# print(parse_csv("a,b\n")) # Should not create an extra record. Expected: [['a', 'b'], []] -> Wait, the rule says "A trailing newline at the end of the input does not create an extra record". This means if we process a line break and then hit EOF immediately, we should discard the final empty list created by the line break logic.

# Re-evaluating the trailing newline:
# If text="a\n", i hits '\n'. Records gets [['a']]. current_record is reset. Loop ends. We shouldn't append another record.

def parse_csv_final(text: str) -> list[list[str]]:
    """Refined version handling trailing newlines correctly."""
    if not text:
        return []

    records = []
    current_record = []
    field_buffer = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        # Check for line endings first, as they dictate record boundaries
        if char == '\r':
            if i + 1 < n and text[i+1] == '\n':
                # Found CRLF (\r\n)
                line_end = True
                i += 2
            else:
                # Found standalone CR (\r)
                line_end = True
                i += 1
        elif char == '\n':
            # Found LF (\n)
            line_end = True
            i += 1
        
        # --- STATE HANDLING (Only if not a line end character itself) ---
        else:
            line_end = False

            if current_record is None: # Initial state check
                current_record = []

            if field_buffer and char == ',':
                # Field separator found
                current_record.append("".join(field_buffer))
                field_buffer = []
                i += 1
                continue

            elif char == '"' and not field_buffer:
                # Start of a quoted field (must be the first non-whitespace character)
                in_quotes = True
                field_buffer.append(char) # Keep the opening quote in buffer for state machine logic below
                i += 1
                continue

            elif char == '"' and field_buffer:
                # Inside a field, but not necessarily quoted (e.g., "a"b). Treat as literal unless we are tracking quotes explicitly.
                # Since the previous block handles starting quotes, if we hit a quote here, it must be part of the content.
                field_buffer.append(char)
                i += 1
                continue

            elif in_quotes:
                # --- INSIDE QUOTES STATE ---
                if char == '"':
                    if i + 1 < n and text[i+1] == '"':
                        # Escaped quote ("")
                        field_buffer.append('"')
                        i += 2
                    else:
                        # Closing quote
                        in_quotes = False
                        i += 1
                else:
                    # Literal character inside quotes
                    field_buffer.append(char)
                    i += 1
            
            else:
                # --- OUTSIDE QUOTES, NORMAL CHARACTER ---
                field_buffer.append(char)
                i += 1

        # --- LINE END PROCESSING (Executed after consuming line break characters) ---
        if line_end:
            record_fields = "".join(field_buffer)
            current_record.append(record_fields)
            
            records.append(current_record[:])
            current_record[:] = []
            field_buffer = []
            in_quotes = False # Reset state machine flags

    # --- POST-PROCESSING (EOF handling) ---
    
    # If we ended the loop and there is content in current_record, it means EOF was reached 
    # without a final newline separator. This completes the last record.
    if field_buffer or current_record:
        current_record.append("".join(field_buffer))
        records.append(current_record[:])

    return records


# Final check on error handling (Malformed input)
# The complexity of detecting malformed quotes requires careful index management, 
# especially when transitioning from quoted state to non-quoted state. 
# We must ensure that if `in_quotes` becomes False due to a closing quote, the subsequent characters are only separators or EOF.

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses CSV text according to RFC-4180 rules from scratch.
    Handles quoted fields, escaped quotes (""), commas, and various line endings.
    Raises ValueError on malformed input.
    """
    if not text:
        return []

    records = []
    current_record = []
    field_buffer = []
    i = 0
    n = len(text)

    # State variables
    in_quotes = False
    start_of_field = True # Tracks if the current field is starting (for initial quote check)

    while i < n:
        char = text[i]
        
        if in_quotes:
            # --- STATE: INSIDE QUOTES ---
            if char == '"':
                # Check for escaped double quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    field_buffer.append('"')
                    i += 2  # Consume both quotes
                    start_of_field = False
                    continue
                else:
                    # Closing quote encountered
                    in_quotes = False
                    i += 1
                    
                    # Check for malformed input immediately after closing quote
                    j = i
                    while j < n and text[j] not in (',', '\n', '\r'):
                        if text[j].strip(): # If we find any non-whitespace char that isn't separator
                            raise ValueError(f"Malformed CSV: Characters found after closing quote at index {i}: '{text[j:]}'")
                        j += 1
                    continue

            else:
                # Any other character inside quotes is literal
                field_buffer.append(char)
                i += 1
                start_of_field = False
        
        else:
            # --- STATE: OUTSIDE QUOTES ---
            if char == '"':
                # Quotes only have special meaning if the field starts with a quote AND we are starting a new field.
                if start_of_field and not field_buffer:
                    in_quotes = True
                    i += 1
                    start_of_field = False # We are now processing content, so it's no longer "starting"
                    continue
                else:
                    # Quote found mid-field (e.g., a"b). Treat as literal text.
                    field_buffer.append(char)
                    i += 1
                    start_of_field = False

            elif char == ',':
                # Field separator found
                current_record.append("".join(field_buffer))
                field_buffer = []
                start_of_field = True
                i += 1

            elif char == '\n' or char == '\r':
                # Line ending detected (must be outside quotes)
                
                is_crlf = (char == '\r' and i + 1 < n and text[i+1] == '\n')
                
                if is_crlf:
                    line_end = True
                    i += 2 # Consume both \r and \n
                elif char == '\n':
                    line_end = True
                    i += 1
                else: # Must be standalone \r
                    line_end = True
                    i += 1

                # Process the completed record (even if empty)
                records.append(current_record[:])
                current_record[:] = []
                field_buffer = []
                start_of_field = True
                continue # Continue loop after processing line end

            else:
                # Regular character
                field_buffer.append(char)
                i += 1
                start_of_field = False

        # If we reached here and processed a non-separator, non-newline char, 
        # ensure the state machine flags are correctly updated (already done above, but good safety check).


    # --- POST-PROCESSING: EOF handling ---
    
    # If there is content buffered, it means EOF was reached without a final newline separator.
    if field_buffer or current_record:
        current_record.append("".join(field_buffer))
        records.append(current_record[:])

    return records
