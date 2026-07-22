import re

def encode(text: str) -> str:
    if not text:
        return ""
    result = []
    count = 1
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            result.append(f"{count}{text[i - 1]}")
            count = 1
    result.append(f"{count}{text[-1]}")
    return "".join(result)

def decode(encoded: str) -> str:
    if not encoded:
        return ""
    return "".join(char * int(count) for count, char in re.findall(r"(\d+)([a-zA-Z])", encoded))
