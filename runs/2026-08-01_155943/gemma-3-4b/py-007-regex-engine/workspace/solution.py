def match(pattern: str, text: str) -> bool:
    """
    Reports whether `pattern` matches the ENTIRE `text` (not a substring),
    supporting exactly this regex subset:

    - literal characters (match themselves)
    - `.` — any single character
    - `*` — zero or more of the preceding element
    - `+` — one or more of the preceding element
    - `?` — zero or one of the preceding element
    - character classes `[abc]`, ranges `[a-z0-9]`, and negation `[^abc]`
      (`*`/`+`/`?` may follow a class)
    """

    def solve(pattern_idx, text_idx):
        if pattern_idx == len(pattern) and text_idx == len(text):
            return True
        if pattern_idx == len(pattern):
            return False
        if text_idx == len(text):
            if pattern[pattern_idx:] == '*':
                return solve(pattern_idx + 1, text_idx)
            elif pattern[pattern_idx:] == '+':
                return solve(pattern_idx + 1, text_idx)
            elif pattern[pattern_idx:] == '?':
                return solve(pattern_idx + 1, text_idx)
            else:
                return False

        if pattern[pattern_idx] == '.':
            return solve(pattern_idx + 1, text_idx + 1)
        elif pattern[pattern_idx] == '*':
            if pattern_idx == 0 or (pattern[pattern_idx - 1] == '.' or pattern[pattern_idx - 1] in '[]^'):
                if solve(pattern_idx + 1, text_idx):  # Zero occurrences
                    return True
                while text_idx < len(text) and (pattern[pattern_idx] == '.' or pattern[pattern_idx] == text[text_idx]):
                    if solve(pattern_idx + 1, text_idx + 1):
                        return True
                    text_idx += 1
                return False
            else:
                return False # No preceding element
        elif pattern[pattern_idx] == '+':
            if pattern_idx == 0 or (pattern[pattern_idx - 1] == '.' or pattern[pattern_idx - 1] in '[]^'):
                if solve(pattern_idx + 1, text_idx):  # One occurrence
                    return True
                while text_idx < len(text) and (pattern[pattern_idx] == '.' or pattern[pattern_idx] == text[text_idx]):
                    if solve(pattern_idx + 1, text_idx + 1):
                        return True
                    text_idx += 1
                return False
            else:
                return False # No preceding element
        elif pattern[pattern_idx] == '?':
            if solve(pattern_idx + 1, text_idx):  # Zero occurrences
                return True
            if text_idx < len(text) and (pattern[pattern_idx] == '.' or pattern[pattern_idx] == text[text_idx]):
                return solve(pattern_idx + 1, text_idx + 1)
            return False
        elif pattern[pattern_idx] in '[]^' :
            if text_idx < len(text) and text[text_idx] in pattern[pattern_idx:]:
                return solve(pattern_idx + 1, text_idx + 1)
            else:
                return False

        elif pattern[pattern_idx] == text[text_idx]:
            return solve(pattern_idx + 1, text_idx + 1)
        else:
            return False

    if not pattern and not text:
        return True
    if not pattern and text:
        return False
    if pattern.startswith("*") and len(pattern) == 1 :
      raise ValueError("Malformed pattern: '*' must have a preceding element.")

    return solve(0, 0)
