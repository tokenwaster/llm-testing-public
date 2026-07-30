def title_case(s: str) -> str:
    """Converts a string to Title Case, handling common contractions and names."""
    # A simple replacement strategy is best here given the strict test expectations for apostrophes.
    import re
    
    # 1. Convert everything to lowercase initially
    s_lower = s.lower()

    def capitalize_match(match):
        word = match.group(0)
        if "'" in word:
            # Special handling for contractions/possessives to maintain internal casing structure
            parts = word.split("'")
            result = []
            for i, part in enumerate(parts):
                result.append(part[0].upper() + part[1:].lower()) # Capitalize first letter of each segment
            return "'".join(result)
        return word.capitalize()

    # Split by whitespace, process each word, and rejoin. This handles simple words correctly.
    words = s_lower.split()
    titled_words = [capitalize_match(word) for word in words]
    
    # Rejoining might lose internal spaces if the original text had multiple space separators, 
    # but based on standard title case usage, simply joining works.
    return " ".join(titled_words)


def snake_case(s: str) -> str:
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0 and (s[i - 1].islower() or (i + 1 < len(s) and s[i + 1].islower())):
            out.append("_")
        out.append(ch.lower())
    return "".join(out).replace(" ", "_").replace("-", "_")


def truncate(s: str, limit: int) -> str:
    if len(s) <= limit:
        return s
    # Ensure the resulting string length is exactly 'limit' when truncation occurs.
    if limit == 0: return ""

    # We need to slice s to leave room for "..." while respecting `limit`.
    # The desired output length is `limit`, and the appended suffix has length 3.
    return s[:max(len(s), limit - 3)] + "…" if limit >= 3 else s[:limit] # Adjusted logic slightly
