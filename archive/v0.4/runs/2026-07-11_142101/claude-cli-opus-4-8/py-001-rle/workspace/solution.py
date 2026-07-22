def encode(text: str) -> str:
    if not text:
        return ""
    result = []
    prev = text[0]
    count = 1
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
    result = []
    num = ""
    for ch in encoded:
        if ch.isdigit():
            num += ch
        else:
            result.append(ch * int(num))
            num = ""
    return "".join(result)
