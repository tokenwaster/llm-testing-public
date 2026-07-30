import re

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses CSV text according to RFC 4180 rules from scratch.

    Args:
        text: The input CSV data string.

    Returns:
        A list of lists, where each inner list is a record (row).

    Raises:
        ValueError: If the input is malformed (e.g., unclosed quotes, 
                    or characters after closing quote that aren't separators/EOF).
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = []
    
    # State variables
    in_quotes = False
    i = 0
    n = len(text)

    def finalize_field():
        """Finalizes the current field and appends it to the record."""
        records.append(list(current_record)) # This is wrong, we are building records here
        # Correction: We append fields to current_record, and when a line ends, 
        # we append current_record to records.

    def finalize_field_and_advance():
        """Finalizes the field, adds it to the current record, and resets."""
        current_record.append("".join(current_field))
        current_field = []

    while i < n:
        char = text[i]
        next_char = text[i+1] if i + 1 < n else None

        # --- Handle Newline/Record Boundary Detection ---
        is_crlf = char == '\r' and next_char == '\n'
        is_lf = char == '\n' and not (next_char == '\r') # Check for standalone LF
        
        if in_quotes:
            # If inside quotes, newlines are literal characters.
            pass 
        elif char == '\n':
            # Handle LF only if it wasn't part of CRLF already processed
            if not is_crlf and not (char == '\r'): # Avoid double counting CR/LF logic
                record_boundary = True
            else:
                record_boundary = False
        elif char == '\r':
            # Handle CR only if it's followed by LF, or if we treat standalone CR as boundary
            if is_crlf:
                record_boundary = True
            else:
                # RFC 4180 generally treats bare CR as a record separator too.
                record_boundary = True
        elif char == ',':
            # Comma always separates fields unless inside quotes
            record_boundary = False
        else:
            record_boundary = False

        if (is_crlf or is_lf) and not in_quotes:
            # Record boundary found outside of quotes.
            
            # 1. Finalize the current field before the newline sequence
            finalize_field_and_advance()
            
            # 2. Start a new record (unless this is the very first line, which is handled by initialization)
            records.append(current_record)
            current_record = []
            
            # 3. Consume the newline characters and move past them
            i += 1 if char == '\r' else 0 # If we hit \r\n, i will advance twice below
            if is_crlf:
                i += 1 # Skip LF
            elif is_lf:
                # This case should ideally not happen if we process line by line correctly, 
                # but since we are character iterating, we just skip the char.
                pass

            i += 1
            continue


        # --- State Machine Logic (Character Processing) ---

        if in_quotes:
            current_field.append(char)
            
            if char == '"':
                if next_char == '"':
                    # Escaped quote "" -> "
                    current_field.append('"')
                    i += 1 # Consume the second quote
                else:
                    # Closing quote
                    in_quotes = False
                    
                    # Check for characters immediately following the closing quote
                    j = i + 1
                    while j < n and text[j] not in (',', '\n', '\r'):
                        raise ValueError(f"Malformed CSV: Characters found after closing quote at index {i}: '{text[j:]}'")

            # If we are inside quotes, we just consume the character and move on.
        
        else: # Not in quotes
            if char == '"':
                # Special meaning only if field starts with a quote AND current_field is empty
                if not current_field:
                    in_quotes = True
                else:
                    # Literal quote character (e.g., 'a"b')
                    current_field.append(char)

            elif char == ',':
                # Field separator found outside quotes
                finalize_field_and_advance()
            
            elif char == '\r' or char == '\n':
                # This should have been caught by the record boundary logic above, 
                # but if we reach here and it's a newline/carriage return, something is wrong 
                # unless it was part of an unquoted field (which is generally invalid CSV structure).
                if not current_field: # If we hit a separator without content, treat as empty field
                    finalize_field_and_advance()
                else:
                    # Treat the newline/CR as literal characters if they are encountered 
                    # outside of quotes and not acting as separators (this is complex, 
                    # but standard CSV parsers usually fail here unless quoted).
                    # Since we handled record boundaries above, hitting this means it's an error or a separator.
                    pass # The boundary logic handles the separation

            else:
                # Regular character
                current_field.append(char)

        i += 1


    # --- Post-Processing and Finalization ---

    # 1. Handle EOF state checks
    if in_quotes:
        raise ValueError("Malformed CSV: Unclosed quote at end of input.")

    # 2. Finalize the last field/record if data was processed
    finalize_field_and_advance()
    records.append(current_record) # Append the very last record

    return records

if __name__ == '__main__':
    # Example tests (for verification, not part of final output)
    print("--- Test 1: Basic ---")
    text1 = 'a,b\nc,d'
    result1 = parse_csv(text1)
    print(f"Input: '{text1}'\nOutput: {result1}") # Expected: [['a', 'b'], ['c', 'd']]

    print("\n--- Test 2: Quotes and Commas ---")
    text2 = 'a,"b,c"\nd,"e""f"'
    result2 = parse_csv(text2)
    print(f"Input: '{text2}'\nOutput: {result2}") # Expected: [['a', 'b,c'], ['d', 'e"f']]

    print("\n--- Test 3: Empty Fields ---")
    text3 = 'a,,b\nc,,,d'
    result3 = parse_csv(text3)
    print(f"Input: '{text3}'\nOutput: {result3}") # Expected: [['a', '', 'b'], ['c', '', '', 'd']]

    print("\n--- Test 4: Newlines and CR/LF ---")
    # Note: The parser must handle newlines inside quotes correctly.
    text4 = 'line1,"multi\nline2",field3\r\nline4'
    result4 = parse_csv(text4)
    print(f"Input: '{repr(text4)}'\nOutput: {result4}") # Expected: [['line1', 'multi\nline2', 'field3'], ['line4']]

    print("\n--- Test 5: Trailing Newline ---")
    # A trailing newline should not create an extra empty record.
    text5 = 'a,b\n'
    result5 = parse_csv(text5)
    print(f"Input: '{repr(text5)}'\nOutput: {result5}") # Expected: [['a', 'b']]

    print("\n--- Test 6: Empty Input ---")
    text6 = ""
    result6 = parse_csv(text6)
    print(f"Input: '{text6}'\nOutput: {result6}") # Expected: []

    print("\n--- Test 7: Single empty line (Record with single empty field) ---")
    # The input must be structured such that the record is created, but fields are empty.
    text7 = "\n"
    result7 = parse_csv(text7)
    print(f"Input: '{repr(text7)}'\nOutput: {result7}") # Expected: [[], []] (Two records if we assume the input is two lines, but since it's just '\n', it should be one empty record followed by another empty record if EOF triggers a finalization.)
    # Correction based on rules: A single newline means an empty field for the first line, and then the second line starts. 
    # If we process "\n", the parser hits boundary -> records=[[]], current_record=[] -> loop ends. Finalize -> records=[[], []] (This is tricky). Let's assume standard CSV behavior: one record of empty fields if only newlines are present.

    print("\n--- Test 8: Malformed Input (Unclosed quote) ---")
    try:
        parse_csv('a,"b')
    except ValueError as e:
        print(f"Caught expected error: {e}")

    print("\n--- Test 9: Malformed Input (Char after closing quote) ---")
    try:
        parse_csv('"ab"x')
    except ValueError as e:
        print(f"Caught expected error: {e}")
