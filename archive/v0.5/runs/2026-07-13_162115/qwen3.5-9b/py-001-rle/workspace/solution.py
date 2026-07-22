def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    count = 1
    
    for i in range(len(text)):
        if i + 1 < len(text) and text[i] == text[i + 1]:
            count += 1
        else:
            result.append(f"{count}{text[i]}")
            count = 1
    
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        # Extract the number (may be multi-digit)
        j = i
        while j < len(encoded) and encoded[j].isdigit():
            j += 1
        
        count = int(encoded[i:j])
        char = encoded[j]
        
        result.append(char * count)
        i = j + 1
    
    return "".join(result)
