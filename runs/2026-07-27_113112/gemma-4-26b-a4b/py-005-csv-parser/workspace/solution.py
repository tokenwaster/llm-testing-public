def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-compliant CSV string from scratch.
    
    Rules implemented:
    - Fields are separated by commas, records by \n or \r\n.
    - Quoted fields can contain commas, newlines, and doubled double-quotes ("").
    - Quotes only have special meaning if the field starts with a quote.
    - Empty fields/records handled according to RFC-4160 (e.g., 'a,,b' -> 3 fields).
    - Malformed input (unclosed quotes or trailing characters after closing quotes) raises ValueError.
    """
    if not text:
        return []

    rows = []
    current_row = []
    i = 0
    n = len(text)

    while i < n:
        field_chars = []
        is_quoted = False

        # Check if the field starts with a double quote
        if text[i] == '"':
            is_quoted = True
            i += 1  # Skip opening quote
            while i < n:
                if text[i] == '"':
                    # Check for doubled double-quotes (escaped quotes)
                    if i + 1 < n and text[i+1] == '"':
                        field_chars.append('"')
                        i += 2
                    else:
                        # End of quoted field
                        is_quoted = False
                        i += 1
                        break
                else:
                    field_chars.append(text[i])
                    i += 1
            
            if is_quoted:
                raise ValueError("Unclosed quote in CSV field")

            # Post-quote validation: must be followed by a separator or EOF
            if i < n and text[i] not in ',\r\n':
                raise ValueError("Unexpected character after closing quote")
        else:
            # Unquoted field logic: read until the next separator
            while i < n and text[i] not in ',\r\n':
                field_chars.append(text[i])
                i += 1
            is_quoted = False

        # Add the processed field to the current row
        current_row.append("".join(field_chars))

        # Handle separators after the field is parsed
        if i < n:
            if text[i] == ',':
                # If comma is at the very end, create an empty trailing field
                if i + 1 == n:
                    current_row.append("")
                i += 1
                # Continue to next field in same row
            elif text[i] == '\r':
                # Handle CRLF or CR
                if i + 1 < n and text[i+1] == '\n':
                    i += 2
                else:
                    i += 1
                rows.append(current_row)
                current_row = []
            elif text[i] == '\n':
                # Handle LF
                i += 1
                rows.append(current_row)
                current_row = []

    # If there's a remaining row that hasn't been pushed (due to no trailing newline), add it
    if current_row:
        rows.append(current_row)

    return rows
