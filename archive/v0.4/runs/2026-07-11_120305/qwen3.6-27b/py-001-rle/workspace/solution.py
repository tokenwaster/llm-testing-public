def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    count = 1
    current_char = text[0]
    
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
    n = len(encoded)
    
    while i < n:
        count = 0
        while i < n and encoded[i].isdigit():
            count = count * 10 + int(encoded[i])
            i += 1
        char = encoded[i]
        i += 1
        result.append(char * count)
        
    return "".join(result)
