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
    
    result.append(f"{count}{current_char}")
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    
    result = []
    i = 0
    while i < len(encoded):
        # Read the count (may be multi-digit)
        j = i
        while j < len(encoded) and encoded[j].isdigit():
            j += 1
        count = int(encoded[i:j])
        char = encoded[j]
        result.append(char * count)
        i = j + 1
    
    return "".join(result)
