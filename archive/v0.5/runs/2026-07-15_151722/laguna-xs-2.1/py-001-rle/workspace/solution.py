def encode(text: str) -> str:
    if not text:
        return ""
    res = []
    current = text[0]
    count = 1
    for c in text[1:]:
        if c == current:
            count += 1
        else:
            res.append(str(count) + current)
            current = c
            count = 1
    res.append(str(count) + current)
    return ''.join(res)


def decode(encoded: str) -> str:
    res = []
    i = 0
    while i < len(encoded):
        j = i
        while j < len(encoded) and encoded[j].isdigit():
            j += 1
        count = int(encoded[i:j])
        char = encoded[j]
        res.append(char * count)
        i = j + 1
    return ''.join(res)
