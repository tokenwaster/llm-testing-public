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
    n = len(encoded)
    
    while i < n:
        count_str = []
        while i < n and encoded[i].isdigit():
            count_str.append(encoded[i])
            i += 1
            
        if not count_str:
            break
            
        count = int("".join(count_str))
        
        if i < n:
            char = encoded[i]
            result.append(char * count)
            i += 1
            
    return "".join(result)
