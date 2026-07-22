def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.

    Rules handled:
    - Fields separated by commas, records by \n or \r\n.
    - Quoted fields handle internal commas, newlines, and "" -> ".
    - Quotes only special if the field starts with them.
    - Empty fields are represented as "".
    - Malformed input raises ValueError.
    """
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    N = len(text)

    while i <= N:
        field_content = ""
        start_of_field = i
        j = i

        # --- 1. Handle Quoted Field Start ---
        if j < N and text[j] == '"':
            j += 1  # Skip opening quote
            in_quotes = True
            field_buffer = []
            
            while j < N:
                char = text[j]
                if char == '"':
                    # Potential end or escaped quote
                    if j + 1 < N and text[j+1] == '"':
                        # Escaped double quote "" -> "
                        field_buffer.append('"')
                        j += 2  # Skip both quotes
                        continue
                    else:
                        # Closing quote found
                        in_quotes = False
                        break
                elif in_quotes:
                    field_buffer.append(char)
                
                j += 1

            if not in_quotes and j < N:
                # Error check: characters after closing quote?
                k = j + 1
                while k < N and text[k] != ',' and text[k] != '\n' and text[k] != '\r':
                    raise ValueError("Malformed CSV: Characters found after closing quote.")

            field_content = "".join(field_buffer)
            i = j + 1  # Move index past the consumed quoted content (and potential delimiters)
        
        # --- 2. Handle Non-Quoted Field ---
        else:
            k = i
            while k < N and text[k] not in (',', '\n', '\r'):
                k += 1
            field_content = text[i:k]
            i = k  # Move index to the delimiter or end of string

        # --- Process Field Content ---
        current_record.append(field_content)
        
        if i >= N:
            # End of file reached, we are done with this record.
            break 
        
        char = text[i]

        if char == ',':
            # Field separated by comma. Move past the comma.
            i += 1
        elif char in ('\n', '\r'):
            # Record break detected.
            
            # Handle CRLF sequence: If we hit \r, and next is \n, consume both.
            if char == '\r' and i + 1 < N and text[i+1] == '\n':
                i += 2  # Consume \r\n
            else:
                i += 1  # Consume just \n or just \r

            # Finalize the record.
            records.append(list(current_record))
            current_record = []
            continue # Restart loop iteration for the next record


    # --- Finalization: Handle the last record if it wasn't terminated by EOL/EOF processing above. ---
    if current_record or (i == N and records):
        records.append(list(current_record))

    return records
