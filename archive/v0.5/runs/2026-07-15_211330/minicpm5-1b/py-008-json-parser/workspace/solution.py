import sys

def skip_whitespace(text, start_idx):
    """Skip whitespace from start_idx."""
    i = 0
    while i < len(text) and (text[i] == ' ' or text[i] == '\t'):
        i += 1
    return i

def find_matching_closing(s, start_idx):
    """Find the index of the matching closing bracket for '{', '[', or '}'.
    Returns None if no match."""
    stack = []
    i = start_idx + 1
    while i < len(s):
        if s[i] == '{':
            stack.append(i)
        elif s[i] == '}':
            if stack:
                start_index = stack.pop()
                return start_index + 1  # index after '{'
            else:
                return None
        i += 1
    return None

def parse_number(s, start_idx):
    """Parse a number string (without quotes) into int or float."""
    i = 0
    sign = 1
    if s[i] == '-':
        sign = -1
        i += 1
    
    # Parse integer part and optional decimal point/fraction
    val = 0
    dot_seen = False
    e_seen = False
    
    for j in range(i, len(s)):
        c = s[j]
        if c.isdigit():
            val = val * 10 + int(c)
        elif c == '.':
            if not dot_seen:
                dot_seen = True
                continue
            # fractional part - we'll handle later as float
        
        if e_seen and j < len(s) and s[j] in 'eE':
            e_seen = False  # reset exponent flag
    
    # Check if the number is integer (no decimal point)
    if dot_seen:
        # We have a fractional part, so convert to float
        return sign * float(val)
    else:
        return sign * int(val)

def parse_value(text, start_idx):
    """Parse a JSON document starting at text[start_idx]."""
    i = skip_whitespace(text, start_idx)
    
    if i == len(text):
        return None
    
    char = text[i]
    
    # Handle strings (JSON literals)
    if char == '"':
        return text[i]  # string literal
    
    # Handle numbers
    elif char.isdigit() or char in 'eE':
        num_str = text[i+1:]
        if not num_str:
            return None
        try:
            num = parse_number(num_str, i)
            return num
        except ValueError:
            return None
    
    # Handle arrays (JSON array: [string, number, ...])
    elif char == '[':
        end_idx = find_matching_closing(text, i) + 1
        content = text[i+1:end_idx-1]
        if not content:
            return None
        
        # Parse until matching closing bracket for the array element
        result = parse_value(content, 0)
        if result is None:
            return None
        return [result]  # array of parsed objects
    
    # Handle objects (JSON object: {key1, value1, key2, ...})
    elif char == '{':
        end_idx = find_matching_closing(text, i) + 1
        content = text[i+1:end_idx-1]
        if not content:
            return None
        
        result = parse_value(content, 0)
        if result is None:
            return None
        # Parse key-value pairs until next colon or closing brace
        while True:
            kv_start = skip_whitespace(text, i)
            if kv_start == len(text):
                break
            
            kv_end = find_matching_closing(text, kv_start) + 1
            key_str = text[kv_start:kv_end-1]
            value = parse_value(text, kv_end)
            if value is None:
                return None
            result[key_str] = value
            i = kv_end
        
        return result
    
    # Handle booleans and null
    elif char == 't' or char == 'f':
        return text[i]
    
    # Handle null (JSON null)
    elif char == 'n':
        return None
    
    # Invalid character
    else:
        return None

def parse(text):
    """Main function to parse JSON document."""
    if not text:
        return None
    
    i = skip_whitespace(text, 0)
    result = parse_value(text, i)
    if result is None:
        return None
    # Convert parsed object to Python type
    def convert(obj):
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert(value) for key, value in obj.items()}
        else:
            return obj
    
    return convert(result)
