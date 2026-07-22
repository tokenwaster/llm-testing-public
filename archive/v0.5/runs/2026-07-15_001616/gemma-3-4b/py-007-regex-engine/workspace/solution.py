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

    Rules:
    - Do not use the `re` module or any other regex library — build the matcher
      yourself (recursive backtracking is the expected approach).
    - Malformed patterns (e.g. an unclosed `[`, or `*` with nothing before it)
      should raise `ValueError`.
    - An empty pattern matches only the empty text.
    """

    def _match_recursive(pattern, text):
        if not pattern:
            return not text

        if not text:
            if len(pattern) == 1 and pattern[0] == '*':
                return True
            else:
                return False

        if len(pattern) == 1:
            return pattern == '.' or pattern == text[0]

        if pattern[0] == '*':
            return _match_recursive(pattern[1:], text) or \
                   (len(text) > 0 and _match_recursive(pattern, text[1:]))
        elif pattern[0] == '+':
            return (len(text) > 0 and _match_recursive(pattern[1:], text[1:]))
        elif pattern[0] == '?':
            return _match_recursive(pattern[1:], text) or \
                   (len(text) > 0 and _match_recursive(pattern, text[1:]))
        elif pattern[0] == '[':
            end = pattern.find(']')
            if end == -1:
                raise ValueError("Unclosed character class")
            char_class = pattern[1:end]
            if len(char_class) == 0:
                raise ValueError("Empty character class")

            for char in text:
                if char in char_class:
                    if _match_recursive(pattern[end + 1:], text[1:]):
                        return True
            return False
        elif pattern[0] == '-':
            if len(text) == 0:
                raise ValueError("Range cannot start with -")

            char = text[0]
            if char < 'a' or char > 'z':
                raise ValueError("Invalid range character")

            end = pattern.find(']')
            if end == -1:
                raise ValueError("Unclosed character class")

            range_str = pattern[1:end]
            start = ord(char)
            end_val = ord(range_str[0])

            for i in range(start, end_val + 1):
                next_char = chr(i)
                if _match_recursive(pattern[end + 1:], text[1:]):
                    return True
            return False


        else:
            if len(text) > 0 and (pattern[0] == '.' or pattern[0] == text[0]):
                return _match_recursive(pattern[1:], text[1:])
            else:
                return False

    return _match_recursive(pattern, text)
