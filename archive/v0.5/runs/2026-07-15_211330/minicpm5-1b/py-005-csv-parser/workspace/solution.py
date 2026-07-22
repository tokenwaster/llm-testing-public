def parse_csv(text: str) -> list[list[str]]:
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        # Handle newline or carriage return as separator
        if char in ('\n', '\r'):
            # End of current field, decode it
            decoded_field = decode_field(current_field)
            result.append(decoded_field)
            # After decoding, we are at the end of a record. 
            # If the decoded field is empty, it represents an empty field.
            if not decoded_field:
                result.append([])
            i += 1
        else:
            # Add character to current field (if not quote)
            if char != '"':
                current_field.append(char)
            
            # Check for quoted fields
            if char == '"' and in_quote:
                # Check if this quote is escaped by looking at the previous character in current_field
                if len(current_field) > 0 and current_field[-1] == '"' and current_field[-2] == '"':
                    # This quote is escaped, so skip adding it
                    pass
                else:
                    current_field.append(char)
            elif char == '"':
                # Opening quote: start a new quoted field
                in_quote = True
            else:
                # Closing quote: end the quoted field
                in_quote = False
    
    return result


def decode_field(field: str) -> list[str]:
    """Decode a CSV field according to RFC-4180 rules."""
    parts = field.split(',')
    decoded = []
    for part in parts:
        if part == "":
            decoded.append("")
        else:
            decoded.append(part)
    return decoded


def parse_csv(text: str) -> list[list[str]]:
    """Parse CSV from scratch without using the csv module."""
    result = []
    i = 0
    n = len(text)
    
    while i < n:
        char = text[i]
        
        # Handle newline or carriage return as separator
        if char in ('\n', '\r'):
            decoded_field = decode_field(current_field)
            result.append(decoded_field)
            # After decoding, we are at the end of a record. 
            # If the decoded field is empty, it represents an empty field.
            if not decoded_field:
                result.append([])
            i += 1
        else:
            # Add character to current field (if not quote)
            if char != '"':
                current_field.append(char)
            
            # Check for quoted fields
            if char == '"' and in_quote:
                # Check if this quote is escaped by looking at the previous character in current_field
                if len(current_field) > 0 and current_field[-1] == '"' and current_field[-2] == '"':
                    # This quote is escaped, so skip adding it
                    pass
                else:
                    current_field.append(char)
            elif char == '"':
                # Opening quote: start a new quoted field
                in_quote = True
            else:
                # Closing quote: end the quoted field
                in_quote = False
    
    return result


# Example usage (not part of the solution, just for testing):
if __name__ == "__main__":
    test_cases = [
        ("", []),
        ("\n", []),
        ("a,b,c", [["a", "b", "c"]]),
        ("a,\nb\nc,d", [["a", "", "b", "c", "d"]]),
        ("ab\"cd\",e,f", [["ab\"cd\", e, f"], [""]]),  # empty field
        ("\n\n", []),
        ("a,,b", [["a", "", "b"]]),
    ]
    
    for text in test_cases:
        print(f"Input: {text}")
        print(f"Output: {parse_csv(text)}")
