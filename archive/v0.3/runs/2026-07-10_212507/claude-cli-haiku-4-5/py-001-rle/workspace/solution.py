def encode(text: str) -> str:
    if not text:
        return ""
    
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        count = 1
        while i + count < len(text) and text[i + count] == char:
            count += 1
        result.append(f"{count}{char}")
        i += count
    
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    
    result = []
    i = 0
    while i < len(encoded):
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if i < len(encoded):
            char = encoded[i]
            count = int(count_str)
            result.append(char * count)
            i += 1
    
    return "".join(result)
