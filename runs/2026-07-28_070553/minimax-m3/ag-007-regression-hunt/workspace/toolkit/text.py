def title_case(s: str) -> str:
    # Capitalize the first character of each whitespace-separated word,
    # and lowercase all remaining letters. Apostrophes are kept in-word.
    def cap_word(word):
        if not word:
            return word
        return word[0].upper() + word[1:].lower()
    return " ".join(cap_word(w) for w in s.split(" "))


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