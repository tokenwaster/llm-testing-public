class Atom:
    def matches(self, char: str) -> bool:
        raise NotImplementedError


class DotAtom(Atom):
    def matches(self, char: str) -> bool:
        return True


class CharAtom(Atom):
    def __init__(self, char: str):
        self.char = char

    def matches(self, char: str) -> bool:
        return char == self.char


class ClassAtom(Atom):
    def __init__(self, char_set: set, negated: bool):
        self.char_set = char_set
        self.negated = negated

    def matches(self, char: str) -> bool:
        if self.negated:
            return char not in self.char_set
        return char in self.char_set


def parse_pattern(pattern: str):
    tokens = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        if c in ('*', '+', '?'):
            raise ValueError(f"Quantifier '{c}' without preceding element")
        elif c == ']':
            raise ValueError("Unmatched ']'")
        elif c == '[':
            close_idx = pattern.find(']', i + 1)
            if close_idx == -1:
                raise ValueError("Unclosed '['")
            class_str = pattern[i + 1 : close_idx]
            i = close_idx + 1

            if class_str.startswith('^'):
                negated = True
                inner = class_str[1:]
            else:
                negated = False
                inner = class_str

            if not inner:
                raise ValueError("Empty character class")

            char_set = set()
            idx = 0
            inner_len = len(inner)
            while idx < inner_len:
                if idx + 2 < inner_len and inner[idx + 1] == '-':
                    start_c = inner[idx]
                    end_c = inner[idx + 2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError(f"Invalid range in character class: {start_c}-{end_c}")
                    for code in range(ord(start_c), ord(end_c) + 1):
                        char_set.add(chr(code))
                    idx += 3
                else:
                    char_set.add(inner[idx])
                    idx += 1
            atom = ClassAtom(char_set, negated)
        elif c == '.':
            atom = DotAtom()
            i += 1
        else:
            atom = CharAtom(c)
            i += 1

        if i < n and pattern[i] in ('*', '+', '?'):
            quantifier = pattern[i]
            i += 1
        else:
            quantifier = None

        tokens.append((atom, quantifier))

    return tokens


def match(pattern: str, text: str) -> bool:
    tokens = parse_pattern(pattern)

    memo = {}

    def solve(token_idx: int, text_idx: int) -> bool:
        state = (token_idx, text_idx)
        if state in memo:
            return memo[state]

        if token_idx == len(tokens):
            res = (text_idx == len(text))
            memo[state] = res
            return res

        atom, quant = tokens[token_idx]

        if quant is None:
            if text_idx < len(text) and atom.matches(text[text_idx]):
                res = solve(token_idx + 1, text_idx + 1)
            else:
                res = False
        elif quant == '?':
            if text_idx < len(text) and atom.matches(text[text_idx]):
                if solve(token_idx + 1, text_idx + 1):
                    memo[state] = True
                    return True
            res = solve(token_idx + 1, text_idx)
        elif quant == '*':
            k = 0
            while text_idx + k < len(text) and atom.matches(text[text_idx + k]):
                k += 1
            res = False
            for count in range(k, -1, -1):
                if solve(token_idx + 1, text_idx + count):
                    res = True
                    break
        elif quant == '+':
            k = 0
            while text_idx + k < len(text) and atom.matches(text[text_idx + k]):
                k += 1
            res = False
            for count in range(k, 0, -1):
                if solve(token_idx + 1, text_idx + count):
                    res = True
                    break
        else:
            res = False

        memo[state] = res
        return res

    return solve(0, 0)
