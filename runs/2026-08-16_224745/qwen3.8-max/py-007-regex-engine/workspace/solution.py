import sys


def match(pattern: str, text: str) -> bool:
    """
    Match `pattern` against the ENTIRE `text` using recursive backtracking.

    Supported syntax:
      - literal characters
      - .       any single character
      - *       zero or more of the preceding element
      - +       one or more of the preceding element
      - ?       zero or one of the preceding element
      - [...]   character class, including ranges and leading ^ for negation

    Raises ValueError for malformed patterns.
    """
    n = len(pattern)

    def parse_class(i):
        # i points at the opening '['
        i += 1
        negated = False

        if i < n and pattern[i] == "^":
            negated = True
            i += 1

        ranges = []

        while i < n and pattern[i] != "]":
            low = pattern[i]
            i += 1

            # A range like a-z, but only if '-' is not the last character
            # before the closing ']'.
            if (
                i < n
                and pattern[i] == "-"
                and i + 1 < n
                and pattern[i + 1] != "]"
            ):
                i += 1
                high = pattern[i]
                i += 1

                if ord(low) > ord(high):
                    raise ValueError("invalid character range")

                ranges.append((low, high))
            else:
                ranges.append((low, low))

        if i == n:
            raise ValueError("unclosed character class")

        if not ranges:
            raise ValueError("empty character class")

        i += 1  # consume closing ']'
        return (negated, tuple(ranges)), i

    tokens = []
    i = 0

    while i < n:
        ch = pattern[i]

        if ch in "*+?":
            raise ValueError("quantifier with nothing before it")

        if ch == ".":
            kind = "dot"
            value = None
            i += 1
        elif ch == "[":
            kind = "class"
            value, i = parse_class(i)
        else:
            kind = "lit"
            value = ch
            i += 1

        min_count = 1
        max_count = 1

        if i < n and pattern[i] in "*+?":
            quantifier = pattern[i]
            i += 1

            if quantifier == "*":
                min_count = 0
                max_count = None
            elif quantifier == "+":
                min_count = 1
                max_count = None
            else:  # quantifier == "?"
                min_count = 0
                max_count = 1

        tokens.append((kind, value, min_count, max_count))

    tokens = tuple(tokens)
    text_len = len(text)

    try:
        sys.setrecursionlimit(
            max(sys.getrecursionlimit(), len(tokens) + 1000)
        )
    except Exception:
        pass

    # Minimum number of text characters required from each token index.
    min_suffix = [0] * (len(tokens) + 1)
    for idx in range(len(tokens) - 1, -1, -1):
        min_suffix[idx] = min_suffix[idx + 1] + tokens[idx][2]

    def atom_matches(kind, value, ch):
        if kind == "lit":
            return ch == value

        if kind == "dot":
            return True

        negated, ranges = value
        for low, high in ranges:
            if low <= ch <= high:
                return not negated

        return negated

    memo = {}

    def dp(token_index, text_index):
        key = (token_index, text_index)
        if key in memo:
            return memo[key]

        if text_len - text_index < min_suffix[token_index]:
            memo[key] = False
            return False

        if token_index == len(tokens):
            result = text_index == text_len
            memo[key] = result
            return result

        kind, value, min_count, max_count = tokens[token_index]

        # Leave at least enough characters for the rest of the pattern.
        needed_after = min_suffix[token_index + 1]
        limit = text_len - text_index - needed_after

        if max_count is not None and max_count < limit:
            limit = max_count

        if limit < 0:
            limit = 0

        # Count how many consecutive characters this atom can match here.
        count = 0
        while count < limit and atom_matches(
            kind, value, text[text_index + count]
        ):
            count += 1

        result = False

        # Greedy ordering: try longer repetitions first, then backtrack.
        for taken in range(count, min_count - 1, -1):
            if dp(token_index + 1, text_index + taken):
                result = True
                break

        memo[key] = result
        return result

    return dp(0, 0)
