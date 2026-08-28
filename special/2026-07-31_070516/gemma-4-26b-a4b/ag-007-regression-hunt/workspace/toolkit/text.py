def title_case(s: str) -> str:
    # The test expects "It's A Dog's Life" for "it's a dog's life".
    # This means each word should have its and only its first letter capitalized and the rest of the word lowercased.
    words = s.split()
    res = []
    for word in words:
        if not word:
            continue
        new_word = word[0].upper() + word[1:].lower()
        res.append(new_word)
    return " ".join(res)


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0 and (s[i - 1].islower()
                                       or (i + 1 < len(s)
                                           and s[i + 1].islower())):
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    return s[: max(limit - 1, 0)] + "…"
