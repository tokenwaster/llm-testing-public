def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
    if not text:
        return ""
    
    result = []
    current_char = text[0]
    count = 1
    
    for i in range(1, len(text)):
        char = text[i]
        if char == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = char
            count = 1
            
    # Append the final run
    result.append(f"{count}{current_char}")
    return "".join(result)


def decode(encoded: str) -> str:
    """Decode a run-length encoded string back to its original form."""
    if not encoded:
        return ""
    
    result = []
    count_str = ""
    
    for char in encoded:
        if char.isdigit():
            count_str += char
        else:
            # Append the character repeated by the accumulated count
            result.append(char * int(count_str))
            count_str = ""
            
    return "".join(result)
