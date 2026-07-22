def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    current_char = text[0]
    count = 1
    
    for char in text[1:]:
        if char == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = char
            count = 1
    
    # Append the last run
    result.append(f"{count}{current_char}")
    
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        # Parse the count (one or more digits)
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if i < len(encoded):
            char = encoded[i]
            i += 1
            result.append(char * int(count_str))
    
    return "".join(result)
