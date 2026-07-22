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
    while i < len(encoded):
        num_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            num_str += encoded[i]
            i += 1
        if i < len(encoded):
            char = encoded[i]
            i += 1
            result.append(char * int(num_str))
    return "".join(result)
