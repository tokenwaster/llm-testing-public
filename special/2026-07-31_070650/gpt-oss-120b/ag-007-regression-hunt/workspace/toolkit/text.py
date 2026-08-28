def title_case(s: str) -> str:
    """Convert *s* to title case.

    Unlike :py:meth:`str.title`, this implementation correctly handles
    apostrophes and does not uppercase letters following them.
    Each word's first character is upper‑cased and the remainder is lower‑cased.
    Words are delimited by whitespace.
    """
    def cap_word(word: str) -> str:
        if not word:
            return ''
        # Preserve the original characters after the first one in lower case.
        return word[0].upper() + word[1:].lower()
    # Split on whitespace to keep spacing consistent with typical title case.
    return ' '.join(cap_word(w) for w in s.split())


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
