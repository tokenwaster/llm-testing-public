def encode(text: str) -> str:
    if not text:
        return ""
    result = []
    count = 1
    prev = text[0]
    for ch in text[1:]:
        if ch == prev:
            count += 1
        else:
            result.append(f"{count}{prev}")
            prev = ch
            count = 1
    result.append(f"{count}{prev}")
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    result = []
    count_str = ""
    for ch in encoded:
        if ch.isdigit():
            count_str += ch
        else:
            count = int(count_str)
            result.append(ch * count)
            count_str = ""
    return "".join(result)
