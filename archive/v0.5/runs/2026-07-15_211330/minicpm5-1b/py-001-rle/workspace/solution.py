def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    i = 0
    while i < len(text):
        count = 1
        j = i + 1
        while j < len(text) and text[j] == text[i]:
            count += 1
            j += 1
        
        if count > 1:
            result.append(f"{count}{text[i]}")
        else:
            result.append(f"<1>{text[i]}")
        
        i = j
    
    return ''.join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    
    result = []
    i = 0
    while i < len(encoded):
        count_str = ''
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        char = encoded[i]
        result.append(char * int(count_str))
        i += 1
    
    return ''.join(result)
