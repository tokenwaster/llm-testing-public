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
    return ''.join(result)

def decode(encoded: str) -> str:
    if not encoded:
        return ""
    result = []
    i = 0
    while i < len(encoded):
        digits = []
        while i < len(encoded) and encoded[i].isdigit():
            digits.append(encoded[i])
            i += 1
        count = int(''.join(digits))
        char = encoded[i]
        result.append(char * count)
        i += 1
    return ''.join(result)
