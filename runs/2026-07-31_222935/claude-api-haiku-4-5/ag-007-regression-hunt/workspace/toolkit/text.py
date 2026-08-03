def title_case(s: str) -> str:
    """Convert string to title case, but don't capitalize after apostrophes."""
    words = s.split()
    result = []
    for word in words:
        # Capitalize first letter, lowercase the rest
        # But we need to handle apostrophes specially
        new_word = ""
        capitalize_next = True
        for ch in word:
            if ch == "'":
                new_word += ch
                capitalize_next = False  # Don't capitalize after apostrophe
            elif capitalize_next:
                new_word += ch.upper()
                capitalize_next = False
            else:
                new_word += ch.lower()
        result.append(new_word)
    return " ".join(result)


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
