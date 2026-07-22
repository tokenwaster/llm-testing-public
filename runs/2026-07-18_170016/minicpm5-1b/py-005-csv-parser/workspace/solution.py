def parse_csv(text: str) -> list[list[str]]:
    fields = []
    current_field = []
    in_quotes = False
    
    i = 0
    while i < len(text):
        ch = text[i]
        
        # Handle newline or carriage return as field separator
        if ch == '\n' or ch == '\r':
            # End of current field (if we are building a field)
            if in_quotes:
                # Check for malformed input: after closing quote, any non-comma/newline should be invalid
                if i < len(text) and text[i] != '\n' and text[i] != '\r':
                    raise ValueError("Malformed input")
            
            # If we have an empty field (current_field is empty), append it as a record
            if not current_field:
                fields.append([])
            else:
                fields.append(current_field)
            
            # Reset for next field
            in_quotes = False
            current_field = []
        
        else:
            # Build characters until we hit comma or newline
            while i < len(text) and text[i] != '\n' and text[i] != '\r':
                if ch == '"' and not in_quotes:
                    # Opening quote: set state for next field
                    in_quotes = True
                
                current_field.append(ch)
                i += 1
            
            # End of current field (if we built any characters or hit comma/newline)
            if current_field:
                fields.append(current_field)
        
        # Check for malformed input: after processing all characters, check trailing characters
        if i < len(text) and text[i] != '\n' and text[i] != '\r':
            raise ValueError("Malformed input")
    
    return fields
