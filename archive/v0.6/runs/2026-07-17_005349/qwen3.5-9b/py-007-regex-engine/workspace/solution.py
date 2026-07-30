def match(pattern: str, text: str) -> bool:
    """
    Match pattern against entire text using recursive backtracking.
    Supports: literals, ., *, +, ?, and character classes [abc], [a-z], [^abc].
    Raises ValueError for malformed patterns.
    """

    def backtrack(p_idx: int, t_idx: int) -> bool:
        # If we've consumed all text, check if pattern is also fully consumed
        if t_idx == len(text):
            return p_idx == len(pattern)

        # If pattern exhausted but text remains, no match
        if p_idx == len(pattern):
            return False

        p_char = pattern[p_idx]

        # Check for quantifier after current element (look ahead)
        is_star = False
        is_plus = False
        is_question = False
        next_idx = p_idx + 1

        # Determine if there's a quantifier following this position
        if next_idx < len(pattern):
            if pattern[next_idx] == '*':
                is_star = True
                next_idx += 1
            elif pattern[next_idx] == '+':
                is_plus = True
                next_idx += 1
            elif pattern[next_idx] == '?':
                is_question = True
                next_idx += 1

        # Determine if current position starts a character class
        is_class = False
        class_start = -1
        class_end = -1
        if p_idx < len(pattern) and pattern[p_idx] == '[':
            is_class = True
            class_start = p_idx
            # Find closing bracket
            depth = 0
            for i in range(p_idx, len(pattern)):
                if pattern[i] == '[':
                    depth += 1
                elif pattern[i] == ']':
                    depth -= 1
                    if depth == 0:
                        class_end = i
                        break

        # If we have a quantifier, the preceding element must be valid
        if is_star or is_plus or is_question:
            # Check that there's an element before the quantifier
            if p_idx == 0 and not is_class:
                raise ValueError("Quantifier * / + / ? with nothing before it")
        
        # If we have a character class, extract its content
        class_content = ""
        if is_class:
            class_content = pattern[class_start + 1:class_end]

        # Match current element (character or class) against text
        matched = False

        if is_class:
            # Character class matching
            if t_idx < len(text):
                t_char = text[t_idx]
                in_class = False
                negated = class_content.startswith('^')
                if negated:
                    inner = class_content[1:]
                else:
                    inner = class_content

                for char_range in split_ranges(inner):
                    start, end = char_range
                    if t_char >= start and t_char <= end:
                        in_class = True
                        break

                matched = in_class
            else:
                matched = False
        elif p_idx < len(pattern) and pattern[p_idx] == '.':
            # Any single character
            matched = t_idx < len(text)
        else:
            # Literal character match
            matched = (t_idx < len(text)) and (text[t_idx] == p_char)

        if not matched:
            return False

        # If quantifier, try matching with it
        if is_star:
            # Zero or more of preceding element
            # Try zero matches first, then one or more
            if backtrack(next_idx, t_idx):  # zero matches
                return True
            # Try consuming at least one character
            if matched and backtrack(next_idx, t_idx + 1):
                return True
            return False

        elif is_plus:
            # One or more of preceding element
            if not matched:
                return False
            # Consume at least one
            if backtrack(next_idx, t_idx + 1):
                return True
            return False

        elif is_question:
            # Zero or one of preceding element
            if backtrack(next_idx, t_idx):  # zero matches
                return True
            if matched and backtrack(next_idx, t_idx + 1):  # one match
                return True
            return False

        else:
            # No quantifier, consume exactly one character
            return backtrack(next_idx, t_idx + 1)

    def split_ranges(s: str) -> list:
        """Split a character class content into ranges like 'a-z', '0-9', etc."""
        ranges = []
        i = 0
        while i < len(s):
            if s[i] == '-':
                # Range - need to find next char
                j = i + 1
                while j < len(s) and s[j] != '-' and s[j] != ']':
                    j += 1
                if j < len(s) and s[j] == '-':
                    # Multi-character range like a-z
                    start = s[i - 1]
                    end = s[j + 1]
                    ranges.append((start, end))
                    i = j + 2
                else:
                    # Hyphen as literal character
                    ranges.append(('-', '-'))
                    i += 1
            elif s[i].isalnum() or s[i] in '.':
                # Single character
                ranges.append((s[i], s[i]))
                i += 1
            else:
                i += 1
        return ranges

    if not pattern and not text:
        return True
    if not pattern and text:
        return False
    if pattern and not text:
        return False

    try:
        return backtrack(0, 0)
    except Exception:
        raise ValueError("Malformed pattern")
