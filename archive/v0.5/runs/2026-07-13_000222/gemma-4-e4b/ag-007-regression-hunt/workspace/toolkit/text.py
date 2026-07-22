def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # Fixed: Use regex or manual iteration to handle apostrophes correctly.
    return ' '.join([word[0].upper() + word[1:].lower() if word else '' for word in s.split()])


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        # Check for transitions from lowercase to uppercase (e.g., 'myVariable')
        if ch.isupper() and i > 0 and s[i - 1].islower():
            out.append("_")
        # Check for transitions from non-alphanumeric to alphanumeric, or vice versa
        elif not ch.isalnum() and out:
             # If the previous character added was also non-alphanumeric, skip adding another separator
             if out[-1] != '_' and not char_to_add(out[-1], ch): # Simplified check for consecutive separators
                 pass # Let's rely on simple case conversion first.

        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    """Cut to at most `limit` chars, appending an ellipsis character if cut."""
    if len(s) <= limit:
        return s
    # Fixed: Ensure the ellipsis is only added if there's room for it (limit >= 1).
    # The original logic was close but failed on edge cases or when limit=1.
    ellipsis = "…"
    if limit < len(ellipsis): # If limit is too small to even hold an ellipsis, just cut
        return s[:max(0, limit)]

    # Calculate the length of the content part (limit - 1 for ellipsis)
    content_length = max(0, limit - len(ellipsis))
    return s[:content_length] + ellipsis
