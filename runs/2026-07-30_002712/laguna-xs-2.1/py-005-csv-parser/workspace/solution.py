def parse_csv(text: str) -> list[list[str]]:
    records = []
    n = len(text)
    i = 0

    while i < n:
        current_record = []
        
        # Skip any leading newlines (to handle multiple linebreaks between records)
        while i < n and text[i] in '\r\n':
            if text[i] == '\r' and i + 1 < n and text[i+1] == '\n':
                i +=2
            else:
                i +=1

        # If we are at EOF, break.
        if i >= n:
            break
        
        while i < n:
            in_quotes = False
            field_chars = []

            # Check if the current position starts with a quote
            if text[i] == '"':
                in_quotes = True
                i += 1

            start_i = i
            escaped_quote = False

            while i < n:
                char = text[i]

                if in_quotes and char == '"':
                    # Check for end of quoted field or an escaped quote.
                    if i + 1 < n and text[i+1] == '"':
                        # Escaped quote, add single " to the field
                        field_chars.append('"')
                        i +=2
                        continue
                    else:
                        in_quotes = False
                        i += 1  # consume closing quote
                        break

                elif not in_quotes and (char == ',' or char in '\r\n'):
                    if not field_chars or field_chars[-1] not in ('\n', '\r'):
                        # Only stop here if this is a comma or newline that isn't part of quoted data.
                        break
                
                else:
                    if char == '\r' and i+1 < n and text[i+1] == '\n':
                        # Skip the \r as part of CRLF, but check whether we're in quotes.
                        if not in_quotes:
                            field_chars.append('\n')  # or skip? Hmm this may need fixing.
                        else:
                            field_chars.append('\r\n'[:])
                        i +=1

                    else:
                        field_chars.append(char)
                    
                i +=1

            # Handle case where we broke out of loop due to comma or newline (not in quotes)
            if not in_quotes and (i >=n or text[i-1] in ', \r\n'):
                current_record.append(''.join(field_chars))
            else:
                raise ValueError("Invalid characters after closing quote")

            # Determine next position. After the comma, continue to next field?
            if i < n and not in_quotes and text[i] == ',':
                i +=1  # skip comma
            elif ...  # need to handle when we've hit newline (end of record)
            else:
                break

        records.append(current_record)
        
        while i < n and text[i] in '\r\n':
            if text[i] == '\r' and i+1 <n and text[i+1]=='\n':
                i +=2
            else:
                i +=1

    return records
