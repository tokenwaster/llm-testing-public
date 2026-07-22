import re

def parse_csv(text: str) -> list[list[str]]:
    """
    Parses an RFC-4180 style CSV string from scratch.
    Handles quoted fields, escaped quotes (""), and various line endings.
    """
    if not text:
        return []

    records = []
    current_record = []
    i = 0
    n = len(text)

    def parse_field():
        nonlocal i
        start_index = i
        field_chars = []
        in_quotes = False
        
        while i < n:
            char = text[i]

            if in_quotes:
                # Inside quotes, look for the closing quote or escaped quote
                if char == '"':
                    # Check for escaped quote ""
                    if i + 1 < n and text[i+1] == '"':
                        field_chars.append('"')
                        i += 2  # Consume both quotes
                        continue
                    else:
                        # Closing quote found
                        in_quotes = False
                        i += 1
                        break # Exit field parsing, the delimiter (comma or newline) will be handled by the caller
                else:
                    field_chars.append(char)
                    i += 1
            else:
                # Outside quotes
                if char == ',':
                    # Field separator found
                    i += 1
                    break # Exit field parsing, delimiter consumed
                elif char == '"' and (start_index == i):
                    # Potential start of a quoted field. Must be at the beginning of the field content.
                    in_quotes = True
                    field_chars.append(char)
                    i += 1
                else:
                    # Normal character or non-starting quote
                    field_chars.append(char)
                    i += 1
        
        return "".join(field_chars)

    def advance_past_delimiter():
        nonlocal i
        if i < n and text[i] == ',':
            i += 1 # Consume comma
            return True
        elif i < n:
            # Must be a newline sequence
            if text[i:i+2] == '\r\n':
                i += 2
            elif text[i] == '\n':
                i += 1
            else:
                # Should not happen if logic is correct, but handles EOF/unexpected char after field
                pass
            return True
        return False

    while i < n:
        # 1. Parse the current field
        field = parse_field()
        current_record.append(field)

        # 2. Check what follows the field (delimiter or EOF)
        if i >= n:
            # End of file reached after processing a field
            break

        # If we are here, it means 'i' points to the character *after* the field content.
        # We must check if this character is a delimiter (comma or newline sequence).
        
        if text[i] == ',':
            # Comma separator found: Field ends, move to next field start
            pass # i already advanced past the comma inside parse_field/advance logic implicitly
        elif text[i-1] in ('\n', '\r'): 
             # This case is tricky. If we hit a newline *after* parsing a field, 
             # it means the field was quoted and contained newlines (handled by state machine).
             # But if the line ends here, we must process the record boundary.
             pass

        # Check for Record Boundary (Comma or Newline)
        if text[i] == ',':
            # Comma separates fields on the same logical line
            pass # i is already positioned correctly for the next field start
        elif text[i:i+2] == '\r\n' or text[i] == '\n':
            # Newline sequence found: Record ends.
            records.append(list(current_record))
            current_record = []
            
            # Advance past the entire line ending sequence
            if text[i:i+2] == '\r\n':
                i += 2
            elif text[i] == '\n':
                i += 1
            else: # Should not happen if i < n
                break

        # If we reached EOF and haven't processed the last record yet, break.
        if i >= n:
             break


    # Handle the final record (which wasn't terminated by a newline)
    if current_record or (not records and text):
        records.append(list(current_record))

    return records
