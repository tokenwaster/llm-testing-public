def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180-style CSV string from scratch.
    
    Rules implemented:
    - Fields are separated by commas; records by \n or \r\n.
    - Quoted fields can contain commas, newlines, and doubled double-quotes ("").
    - Quotes only have special meaning if the field starts with a quote.
    - Empty fields decode to "".
    - Trailing newline at end of input does not create an extra record.
    - An empty line in the middle is one record containing a single empty field.
    - parse_csv("") returns [].
    - Malformed input (unclosed quotes or characters after closing quote) raises ValueError.
    """
    if not text:
        return []

    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    n = len(text)

    while i < n:
        char = text[i]

        if not in_quotes:
            if char == '"':
                # A quote only starts a quoted field if it's at the beginning of the field.
                if current_field == "":
                    in_quotes = True
                else:
                    current_field += char
            elif char == ',':
                current_record.append(current_field)
                current_field = ""
            elif char == '\n' or char == '\r':
                # Handle both \n and \r\n
                if char == '\r' and i + 1 < n and text[i+1] == '\n':
                    i += 1
                current_record.append(current_field)
                records.append(current_record)
                current_record = []
                current_field = ""
            else:
                current_field += char
        else:  # in_quotes is True
            if char == '"':
                # Check for doubled double-quotes ("")
                if i + 1 < n and text[i+1] == '"':
                    current_field += '"'
                    i += 1  # Skip the second quote
                else:
                    # End of quoted field.
                    in_quotes = False
                    # RFC-4180: Characters after a closing quote must be comma, newline, or EOF.
                    if i + 1 < n and text[i+1] not in (',', '\n', '\r'):
                        raise ValueError("Malformed CSV: characters found after closing quote")
            else:
                current_field += char
        i += 1

    # If the loop finished but a quote was left open, it's malformed.
    if in_quotes:
        raise ValueError("Malformed CSV: unclosed quote")

    # If the string did not end with a newline, we must finalize the last field and record.
    if n > 0 and text[-1] not in ('\n', '\r'):
        current_record.append(current_field)
        records.append(current_record)

    return records
