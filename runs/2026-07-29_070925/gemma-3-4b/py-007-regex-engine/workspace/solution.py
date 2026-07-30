def match(pattern: str, text: str) -> bool:
    """
    Reports whether pattern matches the ENTIRE text using a custom regex matcher.

    Supports:
      - literal characters (match themselves)
      - . — any single character
      - * — zero or more of the preceding element
      - + — one or more of the preceding element
      - ? — zero or one of the preceding element
      - character classes [abc], ranges [a-z0-9], and negation [^abc]
    """

    def _match_recursive(pattern_idx, text_idx):
        if pattern_idx == len(pattern):
            return text_idx == len(text)

        if text_idx == len(text):
            if pattern[pattern_idx:] == '*':
                return True
            else:
                return False

        if pattern[pattern_idx] == '*':
            # Zero occurrences
            if _match_recursive(pattern_idx + 1, text_idx):
                return True
            # One or more occurrences
            while text_idx < len(text) and (_match_recursive(pattern_idx + 1, text_idx + 1) or \
                                          (pattern[pattern_idx] == '.' or \
                                           text[text_idx] == pattern[pattern_idx])):
                if _match_recursive(pattern_idx + 1, text_idx + 1):
                    return True
            return False

        elif pattern[pattern_idx] == '+':
            # One or more occurrences
            if text_idx < len(text) and (text[text_idx] == pattern[pattern_idx] or \
                                          pattern[pattern_idx] == '.'):
                if _match_recursive(pattern_idx + 1, text_idx + 1):
                    return True
            return False

        elif pattern[pattern_idx] == '?':
            # Zero or one occurrences
            if _match_recursive(pattern_idx + 1, text_idx):
                return True
            if text_idx < len(text) and (text[text_idx] == pattern[pattern_idx] or \
                                          pattern[pattern_idx] == '.'):
                if _match_recursive(pattern_idx + 1, text_idx + 1):
                    return True
            return False

        elif pattern[pattern_idx] == '.':
            if _match_recursive(pattern_idx + 1, text_idx + 1):
                return True
            return False

        elif pattern[pattern_idx] == '[':
            end_char = pattern.find(']', pattern_idx)
            if end_char == -1:
                raise ValueError("Unclosed character class")
            char_class = pattern[pattern_idx + 1:end_char]
            if text_idx >= len(text) or text[text_idx] not in char_class:
                return False
            if _match_recursive(end_char + 1, text_idx + 1):
                return True
            return False

        elif pattern[pattern_idx].isalpha():
            if text_idx >= len(text) or text[text_idx] != pattern[pattern_idx]:
                return False
            return _match_recursive(pattern_idx + 1, text_idx + 1)

        else:
            if text_idx >= len(text) or text[text_idx] != pattern[pattern_idx]:
                return False
            return _match_recursive(pattern_idx + 1, text_idx + 1)

    return _match_recursive(0, 0)
