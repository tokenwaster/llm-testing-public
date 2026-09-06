def title_case(s: str) -> str:
    if not s:
        return s
    result = []
    for i, ch in enumerate(s):
        if i == 0 or (i > 0 and s[i - 1] == ' '):
            result.append(ch.upper())
        else:
            result.append(ch.lower())
    return "".join(result)
