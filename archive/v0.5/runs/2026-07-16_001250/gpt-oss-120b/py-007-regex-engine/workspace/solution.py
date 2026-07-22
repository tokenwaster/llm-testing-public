# solution.py
from functools import lru_cache
from typing import List, Tuple, Set, Dict, Any


def _parse_pattern(pattern: str) -> List[Dict[str, Any]]:
    """
    Parse the pattern into a list of token dictionaries.
    Each token has:
        - type: 'char', 'dot', or 'class'
        - value: character for 'char', None for 'dot',
                 (set_of_chars, negated) for 'class'
        - quant: None, '*', '+', or '?'
    Raises ValueError for malformed patterns.
    """
    tokens: List[Dict[str, Any]] = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        # ----- element parsing -----
        if c == '.':
            elem_type = 'dot'
            value = None
            i += 1
        elif c == '[':
            i += 1
            if i >= n:
                raise ValueError("Unclosed character class")
            neg = False
            if pattern[i] == '^':
                neg = True
                i += 1
            chars: Set[str] = set()
            if i >= n:
                raise ValueError("Unclosed character class")
            while i < n and pattern[i] != ']':
                if (i + 2 < n) and pattern[i + 1] == '-':
                    start = pattern[i]
                    end = pattern[i + 2]
                    if ord(start) > ord(end):
                        raise ValueError(f"Invalid range {start}-{end}")
                    for code in range(ord(start), ord(end) + 1):
                        chars.add(chr(code))
                    i += 3
                else:
                    chars.add(pattern[i])
                    i += 1
            if i >= n or pattern[i] != ']':
                raise ValueError("Unclosed character class")
            i += 1  # skip closing ']'
            if not chars:
                raise ValueError("Empty character class")
            elem_type = 'class'
            value = (chars, neg)
        elif c in '*+?':
            raise ValueError(f"Quantifier '{c}' without preceding element")
        else:
            elem_type = 'char'
            value = c
            i += 1

        # ----- quantifier handling -----
        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1

        tokens.append({'type': elem_type, 'value': value, 'quant': quant})

    return tokens


def _token_matches(token: Dict[str, Any], ch: str) -> bool:
    """Return True if the token matches the single character ch."""
    ttype = token['type']
    if ttype == 'dot':
        return True
    if ttype == 'char':
        return token['value'] == ch
    if ttype == 'class':
        chars, neg = token['value']
        return (ch not in chars) if neg else (ch in chars)
    return False  # should never happen


def match(pattern: str, text: str) -> bool:
    """
    Return True iff the entire `text` matches `pattern`.
    Supported constructs:
        literals, ., *, +, ?, character classes with ranges and negation.
    Raises ValueError for malformed patterns.
    """
    tokens = _parse_pattern(pattern)

    @lru_cache(maxsize=None)
    def dfs(tok_idx: int, txt_idx: int) -> bool:
        # If we've consumed all tokens, text must also be fully consumed.
        if tok_idx == len(tokens):
            return txt_idx == len(text)

        token = tokens[tok_idx]
        quant = token['quant']

        # ----- no quantifier -----
        if quant is None:
            if txt_idx < len(text) and _token_matches(token, text[txt_idx]):
                return dfs(tok_idx + 1, txt_idx + 1)
            return False

        # ----- '?' quantifier -----
        if quant == '?':
            # zero occurrence
            if dfs(tok_idx + 1, txt_idx):
                return True
            # one occurrence
            if txt_idx < len(text) and _token_matches(token, text[txt_idx]):
                return dfs(tok_idx + 1, txt_idx + 1)
            return False

        # ----- '*' or '+' quantifier -----
        # Determine the minimal number of required matches.
        min_rep = 1 if quant == '+' else 0

        # First, ensure we have at least `min_rep` matches.
        cur = txt_idx
        for _ in range(min_rep):
            if cur < len(text) and _token_matches(token, text[cur]):
                cur += 1
            else:
                return False

        # Now we can match any additional repetitions (including zero).
        # Greedy backtracking: try the longest possible stretch first.
        max_pos = cur
        while max_pos < len(text) and _token_matches(token, text[max_pos]):
            max_pos += 1

        # Try all possible split points from longest to shortest.
        for split in range(max_pos, cur - 1, -1):
            if dfs(tok_idx + 1, split):
                return True
        return False

    return dfs(0, 0)
