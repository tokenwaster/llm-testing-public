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
        if encoded[i].isdigit():
            num_str = ""
            while i < len(encoded) and encoded[i].isdigit():
                num_str += encoded[i]
                i += 1
            
            count = int(num_str)
            
            if i < len(encoded):
                char = encoded[i]
                result.append(char * count)
                i += 1
        else:
            result.append(encoded[i])
            i += 1
    
    return "".join(result)
