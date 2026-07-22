def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # FIX: Use a more careful approach than s.title() to avoid capitalizing after apostrophes.
    words = s.split(" ")
    result = []
    for word in words:
        if not word:
            result.append("")
            continue
        # Capitalize first letter, lowercase the rest of the word
        # But we need to be careful about internal apostrophes.
        # Actually, title_case("o'neill's") == "O'neill's" implies only the very first char is capitalized.
        # Wait, let's re-read: "Capitalize the first letter of each word, lowercase the rest."
        # "it's a dog's life" -> "It's A Dog's Life"
        # This means for each space-separated word, capitalize only the very first character.
        new_word = word[0].upper() + word[1:].lower()
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
    """Cut to at most `limit` chars, appending an ellipsis character if cut."""
    if len(s) <= limit:
        return s
    return s[: max(limit - 1, 0)] + "…"
