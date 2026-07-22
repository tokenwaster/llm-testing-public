def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    count = 1
    current_char = text[0]
    
    for i in range(1, len(text)):
        if text[i] == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = text[i]
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
        num_str = ""
        while i < n and encoded[i].isdigit():
            num_str += encoded[i]
            i += 1
        if i < n:
            char = encoded[i]
            i += 1
            count = int(num_str)
            result.append(char * count)
    return "".join(result)
