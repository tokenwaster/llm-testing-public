import sys

def parse(text: str):
    """
    Parses a JSON document string without using json module.
    Returns equivalent Python object or None on invalid input.
    """
    
    def skip_whitespace(s, i):
        """Skip whitespace characters starting from position i."""
        while i < len(s) and s[i] in '\t\n\r':
            i += 1
        return i

    def parse_value(s, i):
        """Parse a value until newline or end of string."""
        if i >= len(s):
            return None
        
        # Skip whitespace
        skip_whitespace(s, i)
        
        c = s[i]
        result = None
        
        # Handle boolean true/false
        if c in ('t', 'f'):
            # Check for escaped characters? Not needed here since we're not using json module.
            # Actually we should handle Unicode escapes later when parsing strings.
            continue  # Assume valid JSON bool, return True/False directly (as Python boolean)
        
        # Handle null
        if c == 'n':
            result = None
            i += 1
            continue
        
        # Handle single quote for string starts
        if c == '"':
            # Check for escaped single quotes in JSON strings
            # Look ahead to see if there's \\u followed by hex digits
            j = i + 1
            while j < len(s) and s[j] != '\\' and (s[j] not in '0123456789abcdefABCDEF'):
                j += 1
            
            # If we found a single quote preceded by \u (two backslash, u)
            if j > i + 2:
                # The single quote is escaped: skip the two backslashes and u for parsing purposes
                i += 3  # skip backslash, u, and space? Actually we need to advance past the escape sequence.
                # But careful: in JSON, the escape is written as \\u, so after a double quote we might see \\u followed by hex digits.
                # So if s[i] == '"' and i+1 < len(s) and s[i+1] == '\\', then we are at an escaped single quote.
                # We'll skip these three characters (backslash, u, space) to avoid parsing them as part of the string.
                i += 3
            continue
        
        # Handle Unicode escapes in JSON strings: \u followed by hex digits
        if c == '\\' and j < len(s):
            # Check for \u sequence
            if s[j:j+2] == '\\u':
                # Parse hex escape as a single character with unicode conversion
                # Hex digit is 0-9, then A-F or a-f
                k = i + 4
                while k < len(s) and s[k].upper() in 'ABCDEFabcdef':
                    result += chr(ord('0') + (int(s[k], 16)))
                    k += 1
            else:
                # Simple backslash character
                result += c
            
            i += 2  # skip the backslash after \u
        else:
            # If we see a single quote, it's part of string literal or already handled
            if c in ('n', 't'):
                # Already handled above for null/true/false
                continue
            
            # Otherwise, treat as string (with possible Unicode escape)
            result = parse_string(s, i)  # Will be implemented below
        
        return result
    
    def parse_string(s, i):
        """Parse a JSON string until end of string."""
        # Skip whitespace
        skip_whitespace(s, i)
        
        start = i + 1
        if start >= len(s):
            return None
        
        # Check for escaped single quotes (\\u followed by hex digits)
        j = start
        while j < len(s) and s[j] not in ('"', '\\', 'n'):
            j += 1
            
        # If we found a backslash followed by u, then this is an escaped single quote
        if j >= len(s) or (s[j] == '\\' and j+1 < len(s) and s[j+1] == 'u'):
            # Skip the backslash and u to avoid parsing them as part of string
            i += 3  # skip backslash, space, u? Actually we need to advance past the escape sequence.
            # But careful: the escape is \\u, so after a double quote we might see \\ followed by u.
            # In JSON string literal, it's written as \\u, which includes one backslash and one 'u'.
            # So if s[j] == '\\' and j+1 < len(s) and s[j+1] == 'u', then skip these three characters.
            i += 3
        else:
            # Parse the string literal until closing quote
            while start <= j and s[start] != '"':
                start += 1
            
            if start >= len(s):
                return None
            
            result = s[start]
            i = start + 1
            result += '"'
            continue
        
        # Otherwise, treat as normal string (no escape handling)
        if result is not None:
            return parse_value(s, i)  # This would be for non-string values? Actually we are parsing strings only.
        
        # If no quote found, return empty string or null? In JSON, strings must have quotes.
        # So we should return None? But the input might be a valid JSON object without explicit string.
        # We'll assume that if there's no quote at start, it's an error (trailing garbage).
        return None
    
    # Main parsing logic
    i = 0
    obj = parse_value(text, i)
    
    # Check for trailing whitespace or end of string
    if i < len(s):
        while i < len(s) and s[i].isspace():
            i += 1
        
    return obj

# Example usage (not part of the solution, just to show how it works)
if __name__ == "__main__":
    test_cases = [
        '{"key": null}',
        "['a', b']",  # This is a list in JSON syntax, not valid JSON
        '""hello world"""',  # Valid string with escape and Unicode? Not valid because it's not escaped properly.
        '123',  # Integer
        '-5.67e-3',  # Exponent negative number
        '\u00e9 é',  # Unicode escape
        '"n'  # Invalid (no closing quote)
    ]
    
    for case in test_cases:
        parsed = parse(case)
        print(f"{case!r} -> {parsed}")
