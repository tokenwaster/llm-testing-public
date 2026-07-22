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
    count_str = []
    for char in encoded:
        if char.isdigit():
            count_str.append(char)
        else:
            result.append(char * int("".join(count_str)))
            count_str = []
    return "".join(result)
