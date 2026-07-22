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
    count = 0
    for char in encoded:
        if char.isdigit():
            count = count * 10 + int(char)
        else:
            result.append(char * count)
            count = 0
    return "".join(result)
