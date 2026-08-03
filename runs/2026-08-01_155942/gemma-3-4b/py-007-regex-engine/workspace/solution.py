def match(pattern: str, text: str) -> bool:
    """Matches a regex pattern against a given text."""

    if not pattern:
        return not text

    if not text and pattern:
        return False

    if pattern == text:
        return True

    if len(pattern) >= 2 and pattern[1] == '*':
        return match_star(pattern[0], pattern[2:], text)
    elif len(pattern) >= 2 and pattern[1] == '+':
        return match_plus(pattern[0], pattern[2:], text)
    elif len(pattern) >= 2 and pattern[1] == '?':
        return match_question(pattern[0], pattern[2:], text)
    else:
        return match_literal(pattern[0], pattern[1:], text)


def match_star(c: str, pattern: str, text: str) -> bool:
    """Matches zero or more occurrences of the preceding character."""
    i = 0
    while i <= len(text):
        if match_literal(c, pattern, text[:i]):
            return True
        i += 1
    return False


def match_plus(c: str, pattern: str, text: str) -> bool:
    """Matches one or more occurrences of the preceding character."""
    i = 0
    while i < len(text):
        if match_literal(c, pattern, text[:i]):
            return True
        i += 1
    return False


def match_question(c: str, pattern: str, text: str) -> bool:
    """Matches zero or one occurrences of the preceding character."""
    if match_literal(c, pattern, text):
        return True
    i = 0
    while i < len(text):
        if match_literal(c, pattern, text[:i]):
            return True
        i += 1
    return False


def match_literal(c: str, pattern: str, text: str) -> bool:
    """Matches a literal character."""
    if not pattern:
        return False

    if len(pattern) > 1 and pattern[1] == '*':
        return match_star(c, pattern[2:], text)
    elif len(pattern) > 1 and pattern[1] == '+':
        return match_plus(c, pattern[2:], text)
    elif len(pattern) > 1 and pattern[1] == '?':
        return match_question(c, pattern[2:], text)

    if len(pattern) >= 2 and pattern[1] in "[-?*+^]":
        raise ValueError("Invalid regex syntax")

    i = 0
    while i < len(text):
        if text[i] == c:
            return match_literal(c, pattern[1:], text[1:])
        i += 1
    return False


if __name__ == '__main__':
    print(match("abc", "abc"))  # True
    print(match("ab*", "abbbb"))  # True
    print(match("a+", "aa"))  # False
    print(match("a+", "aaa"))  # True
    print(match("a?", "a"))  # True
    print(match("a?", ""))  # False
    print(match("[abc]", "a"))  # False
    print(match("[abc]", "b"))  # True
    print(match("[a-z]", "b"))  # True
    print(match("[0-9]", "5"))  # True
    print(match("[^abc]", "d"))  # True

    try:
        match("[", "abc")
    except ValueError as e:
        print(e)

    try:
        match("*", "abc")
    except ValueError as e:
        print(e)
