import re

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.

    Args:
        text: The input CSV content string.

    Returns:
        A list of lists, where each inner list represents a record (row),
        and strings within are the decoded fields.

    Raises:
        ValueError: If the input contains malformed CSV data (e.g., unclosed quotes).
    """
    if not text:
        return []

    records = []
    current_record_fields = []
    i = 0
    text_len = len(text)

    def finalize_field(start_index, end_index):
        """Extracts and decodes a field segment."""
        segment = text[start_index:end_index]
        if not segment:
            return "" # Handles empty fields resulting from leading/trailing delimiters or consecutive commas

        if segment.startswith('"'):
            # Quoted field decoding
            value = segment[1:]
            decoded_chars = []
            j = 0
            while j < len(value):
                if value[j] == '"':
                    if j + 1 < len(value) and value[j+1] == '"':
                        # Escaped quote "" -> "
                        decoded_chars.append('"')
                        j += 2
                    else:
                        # Closing quote or error condition
                        decoded_chars.append('"')
                        j += 1
                elif value[j] in ('\r', '\n', ','):
                    # Allowed characters within quotes (including delimiters)
                    decoded_chars.append(value[j])
                    j += 1
                else:
                    # Literal character inside quotes
                    decoded_chars.append(value[j])
                    j += 1
            return "".join(decoded_chars)

        else:
            # Unquoted field (no special decoding needed, just slicing)
            return segment

    def start_new_record():
        """Finalizes the current record and starts a new one."""
        nonlocal records, current_record_fields
        if current_record_fields is not None:
            records.append(list(current_record_fields))
            current_record_fields = []

    while i <= text_len:
        # 1. Check for record terminator (EOL sequence) outside quotes
        is_at_eol = False
        if i + 1 < text_len and text[i:i+2] in ('\r\n', '\n'):
            # EOL found. Consume it, but only if not inside an ongoing field that started with quotes.
            # Since we process fields iteratively, the state machine structure handles this implicitly.
            pass # Let the main loop handle the boundary detection

        if current_record_fields is None:
             current_record_fields = []


        # 2. Check if EOL sequence marks end of record and content remaining (EOF check)
        if i >= text_len:
            break

        # --- State Machine Logic for Field Parsing ---
        field_start_i = i
        in_quotes = False
        field_end_i = -1 # Exclusive end index of the field content found so far
        j = i

        # Check if we are starting a quoted field
        if text[j] == '"':
            in_quotes = True
            k = j + 1
            start_content_index = k
            
            while k < text_len:
                char = text[k]
                
                if char == '"':
                    # Potential end quote or escaped quote
                    if k + 1 < text_len and text[k+1] == '"':
                        # Escaped quote "" -> skip two characters
                        k += 2
                    else:
                        # Closing quote found. The field ends here *unless* we hit EOL/Comma immediately after.
                        field_end_i = k + 1 # End index is right AFTER the closing quote
                        break
                elif char in (',', '\n', '\r'):
                    # Allowed delimiters inside quotes, just treat as content
                    pass
                else:
                    k += 1
            else:
                 # Loop completed without finding a closing quote
                 raise ValueError("Unclosed quoted field.")

        elif text[j] == ',':
             field_end_i = j # Empty field before comma
        else:
            # Unquoted field parsing
            k = j
            while k < text_len and text[k] not in (',', '\n', '\r'):
                k += 1
            field_end_i = k

        current_field_value = finalize_field(field_start_i, field_end_i)

        # Handle record/field boundaries based on what character followed the field content
        if text[field_end_i] == ',':
            # Field ended due to comma (delimiter)
            current_record_fields.append(current_field_value)
            i = field_end_i + 1 # Skip comma
            continue

        elif field_end_i >= text_len:
            # EOF reached after processing a final field
            current_record_fields.append(current_field_value)
            break

        elif text[field_end_i] == '\n' or (text[field_end_i-1:].startswith('\r') and text[field_end_i] == '\n'):
            # Record end found (EOL). We must first check if we are at the very beginning of a line.
            
            # Check for CR LF sequence: \r\n
            if text[field_end_i-1] == '\r' and text[field_end_i] == '\n':
                eol_consumed = 2
                EOL_MARKER = "\r\n"
            elif text[field_end_i] == '\n':
                eol_consumed = 1
                EOL_MARKER = "\n"
            else: # Should not happen if logic is correct, but fallback safety check.
                 eol_consumed = 0

            # Check for an empty line marker (e.g., `a,,b\n\n`)
            if field_end_i > 0 and text[field_end_i-1] == '\n' or \
               (text[field_end_i-2:field_end_i] == '\r\n'):

                # Special case handling for empty lines (e.g., input ending in a sequence of delimiters followed by EOL)
                if field_start_i < field_end_i - eol_consumed and \
                   text[field_start_i:field_end_i-eol_consumed].strip() == "" :

                    # If the content parsed for this "field" was empty, 
                    # and we are now at a line break boundary (and haven't appended anything yet),
                    # it signifies an empty record or continuation of delimiters.
                     pass # Handled by setting i below

            current_record_fields.append(current_field_value)
            records.append(list(current_record_fields))
            current_record_fields = []
            i = field_end_i + eol_consumed
            continue

        else:
             # This path should ideally only be hit if the loop structure is faulty, 
             # but conceptually means we finished a segment and now advance i.
             pass


    # --- Re-implementing with clearer line/field extraction logic using index traversal ---

    records = []
    current_record_fields = []
    i = 0
    text_len = len(text)
    
    def decode_field(start, end):
        """Decodes the segment text[start:end] which is guaranteed to be a single field."""
        segment = text[start:end]

        if not segment:
            return "" # Empty field due to consecutive delimiters or empty line content

        if segment.startswith('"'):
            # Quoted field decoding
            content = segment[1:]
            decoded_chars = []
            j = 0
            while j < len(content):
                char = content[j]
                if char == '"':
                    if j + 1 < len(content) and content[j+1] == '"':
                        # Escaped quote "" -> "
                        decoded_chars.append('"')
                        j += 2
                    else:
                        # Closing quote must be followed by delimiter or EOF
                        j += 1
                elif char in ('\r', '\n', ','):
                    # Allowed characters within quotes
                    decoded_chars.append(char)
                    j += 1
                else:
                    # Literal character inside quotes
                    decoded_chars.append(char)
                    j += 1
            return "".join(decoded_chars)
        else:
            # Unquoted field
            return segment


    while i < text_len:
        field_start = i
        
        # Try to find the end of the current field (which might be a comma or EOL marker)
        if text[i] == '"':
            # We are parsing a quoted field. Find the closing quote index first.
            j = i + 1
            while j < text_len:
                char = text[j]
                if char == '"':
                    if j + 1 < text_len and text[j+1] == '"':
                        # Skip escaped quotes, they are content, continue search
                        j += 2
                        continue
                    else:
                        # Potential closing quote found. Check what follows it.
                        next_char = text[j+1:]
                        if not next_char or next_char[0] in (',', '\n', '\r'):
                            field_end = j + 1 # End index is right AFTER the closing quote
                            break
                        else:
                             # Found a closing quote, but non-delimiter characters follow (e.g., "ab"x)
                             raise ValueError("Unexpected character after closing quotes.")

                elif char in ('\r', '\n', ','):
                    pass # Allowed content, continue search
                
                j += 1
            else:
                 # If loop finishes without break, the quote was never closed.
                 raise ValueError("Unclosed quoted field.")
            
            i = field_end + 1

        elif text[i] == ',':
             field_end = i # Empty field before comma
             i += 1
        else:
            # Unquoted field, ends at the first delimiter (comma or EOL)
            k = i
            while k < text_len and text[k] not in (',', '\n', '\r'):
                k += 1
            field_end = k
            i = k

        # If we reached here, field_start to field_end defines the current field.
        current_field_value = decode_field(field_start, i)
        current_record_fields.append(current_field_value)

        # Check for record termination (EOL sequence). This must be outside of quotes if we are handling multi-line content, 
        # but since we already advanced 'i' past the field delimiters, we check here.
        if i >= text_len:
            break # EOF reached after processing last field

        elif text[i] == '\n':
             # EOL found (could be \r\n or just \n).
             # We process the record and advance 'i' past all consumed EOL characters.
             records.append(list(current_record_fields))
             current_record_fields = []

             if text[i-1] == '\r':
                 # Consumed \r\n, move two steps back to handle the actual newline consumption logic 
                 # (Since i was advanced by 'field_end' which stopped at \n)
                i += 1 # Consume the final \n marker

             else:
                i += 1 # Consume only the \n marker
        
        elif text[i] == '\r':
            # Handle case where LF is not present, but CR might signal EOL in some contexts.
            # We assume standard CSV dictates that either \n or \r\n terminates a record outside quotes.
            if i + 1 < text_len and text[i+1] == '\n': # Should have been caught as \r\n above, but safety check
                records.append(list(current_record_fields))
                current_record_fields = []
                i += 2 # Consume both \r and \n
            else:
                # Assume standalone CR is not a record separator unless followed by EOF/data stream logic dictates it.
                 pass


    # After loop termination, process the last remaining record if fields were gathered
    if current_record_fields is not None:
        records.append(list(current_record_fields))

    return records
