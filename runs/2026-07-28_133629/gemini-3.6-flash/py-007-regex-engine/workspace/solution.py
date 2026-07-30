from functools import lru_cache


class Element:
    def matches(self, char: str) -> bool:
        raise NotImplementedError


class DotElement(Element):
    def matches(self, char: str) -> bool:
        return True


class CharElement(Element):
    def __init__(self, char: str):
        self.char = char

    def matches(self, char: str) -> bool:
        return char == self.char


class ClassElement(Element):
    def __init__(self, allowed: set, negated: bool):
        self.allowed = allowed
        self.negated = negated

    def matches(self, char: str) -> bool:
        if self.negated:
            return char not in self.allowed
        else:
            return char in self.allowed


def parse_pattern(pattern: str):
    nodes = []
    i = 0
    n = len(pattern)

    while i < n:
        ch = pattern[i]

        if ch in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{ch}' without preceding element")

        if ch == '.':
            elem = DotElement()
            i += 1
        elif ch == '[':
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class '['")

            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1

            close_idx = pattern.find(']', i)
            if close_idx == -1:
                raise ValueError("Unclosed character class '['")

            content = pattern[i:close_idx]
            if not content:
                raise ValueError("Empty character class")

            allowed = set()
            k = 0
            len_c = len(content)
            while k < len_c:
                if k + 2 < len_c and content[k + 1] == '-':
                    start = content[k]
                    end = content[k + 2]
                    if ord(start) > ord(end):
                        raise ValueError(f"Invalid range '{start}-{end}' in character class")
                    for code in range(ord(start), ord(end) + 1):
                        allowed.add(chr(code))
                    k += 3
                else:
                    allowed.add(content[k])
                    k += 1

            elem = ClassElement(allowed, negated)
            i = close_idx + 1
        else:
            elem = CharElement(ch)
            i += 1

        if i < n and pattern[i] in ('*', '+', '?'):
            quant = pattern[i]
            i += 1
            if i < n and pattern[i] in ('*', '+', '?'):
                raise ValueError("Multiple consecutive quantifiers")
        else:
            quant = '1'

        nodes.append((elem, quant))

    return nodes


def match(pattern: str, text: str) -> bool:
    nodes = parse_pattern(pattern)

    @lru_cache(maxsize=None)
    def backtrack(node_idx: int, text_idx: int) -> bool:
        if node_idx == len(nodes):
            return text_idx == len(text)

        elem, quant = nodes[node_idx]

        if quant == '1':
            if text_idx < len(text) and elem.matches(text[text_idx]):
                return backtrack(node_idx + 1, text_idx + 1)
            return False

        elif quant == '?':
            if text_idx < len(text) and elem.matches(text[text_idx]):
                if backtrack(node_idx + 1, text_idx + 1):
                    return True
            return backtrack(node_idx + 1, text_idx)

        elif quant == '*':
            max_m = 0
            curr = text_idx
            while curr < len(text) and elem.matches(text[curr]):
                max_m += 1
                curr += 1
            for k in range(max_m, -1, -1):
                if backtrack(node_idx + 1, text_idx + k):
                    return True
            return False

        elif quant == '+':
            max_m = 0
            curr = text_idx
            while curr < len(text) and elem.matches(text[curr]):
                max_m += 1
                curr += 1
            for k in range(max_m, 0, -1):
                if backtrack(node_idx + 1, text_idx + k):
                    return True
            return False

        return False

    return backtrack(0, 0)
