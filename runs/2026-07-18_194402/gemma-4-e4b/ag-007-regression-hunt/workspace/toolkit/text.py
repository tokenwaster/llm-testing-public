def title_case(s: str) -> str:
    """Capitalize the first letter of each word, lowercase the rest.
    Words are separated by spaces; internal apostrophes stay untouched
    (``it's`` -> ``It's``, never ``It'S``)."""
    # Use a regex or careful splitting/joining to handle apostrophes correctly.
    # A simple approach is to split by space and then title-case each part, 
    # but we must preserve internal structure like "it's".

    parts = s.split(' ')
    result = []
    for part in parts:
        if not part:
            result.append("")
            continue
        
        # Handle capitalization within the word while preserving apostrophes
        # We capitalize the first character, and then iterate over the rest 
        # to lowercase everything except characters immediately following an apostrophe 
        # (which should remain untouched if they were already capitalized).
        
        # A simpler way that respects the rule: title-case only on non-apostrophe boundaries.
        # Since we are told "it's" -> "It's", standard title() fails because it treats 'S' as a word start.
        
        temp_chars = []
        capitalize_next = True # Start by capitalizing the first char of the part
        for i, char in enumerate(part):
            if capitalize_next and char.isalpha():
                temp_chars.append(char.upper())
                capitalize_next = False
            elif char == "'":
                temp_chars.append(char)
                # Do not reset capitalization state after an apostrophe, 
                # as the next letter might be part of a word continuation (e.g., "it's").
                # However, if we want 'S' to remain capitalized in "It'S" -> "It's", 
                # we must lowercase it unless it is the start of a new word.
                # The requirement says: internal apostrophes stay untouched (``it's`` -> ``It's``).
                # This implies that only the first letter of the *word* should be capitalized, 
                # and everything else should be lowercase, even if it was originally uppercase after an apostrophe.
                capitalize_next = True # Treat next char as potentially starting a new word/segment
            else:
                temp_chars.append(char.lower())
                capitalize_next = False

        result.append("".join(temp_chars))

    return " ".join(result)


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        # Check for transitions from lowercase to uppercase (e.g., 'aB') 
        # or transitions from non-word character to word character (handled by space/hyphen replacement later).
        if ch.isupper() and i > 0:
            prev_char = s[i - 1]
            # Insert underscore if previous char was lowercase, OR if it's the start of a new "word" segment
            # (e.g., 'HTTPResponse' -> 'http_response'). We only insert if prev is lower or non-alpha/digit boundary.
            if prev_char.islower() or not prev_char.isalnum():
                out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    """Cut to at most `limit` chars, appending an ellipsis character if cut."""
    if len(s) <= limit:
        return s
    # Ensure we leave space for the ellipsis '…' (3 characters). 
    # The maximum length of the content part should be limit - 1.
    content_limit = max(0, limit - 1)
    return s[:content_limit] + "…"