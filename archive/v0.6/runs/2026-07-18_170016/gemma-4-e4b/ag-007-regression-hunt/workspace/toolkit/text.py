def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # Use a regex or careful split/join to handle apostrophes correctly.
    # Simple approach: capitalize only after non-alphanumeric separators (like space)
    return ' '.join([word[0].upper() + word[1:].lower() for word in s.split()])


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        # Check if current char is upper AND it's not the start of the string
        # AND (previous char was lower OR next char exists and is lower)
        if ch.isupper() and i > 0 and (s[i - 1].islower() or (i + 1 < len(s) and s[i + 1].islower())):
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    """Cut to at most `limit` chars, appending an ellipsis character if cut."""
    if len(s) <= limit:
        return s
    # Ensure we leave space for the ellipsis '…' (3 characters).
    # The original implementation was correct in its logic but maybe too complex.
    # Let's simplify and ensure we don't exceed `limit` including the ellipsis.
    if limit < 3: # Handle very small limits gracefully
        return s[:max(0, limit)]

    return s[:limit - 1] + "…"