def match(pattern: str, text: str) -> bool:
    # Parse pattern into tokens: (kind, value, negate, quant)
    # kind: 'lit' | 'dot' | 'class'
    tokens = []
    n = len(pattern)
    i = 0
    while i < n:
        c = pattern[i]
        if c in ('*', '+', '?'):
            raise ValueError(f"quantifier '{c}' with nothing before it")
        elif c == '[':
            j = i + 1
            negate = False
            if j < n and pattern[j] == '^':
                negate = True
                j += 1
            closing = pattern.find(']', j)
            if closing == -1:
                raise ValueError("unclosed '['")
            if closing == j:
                raise ValueError("empty character class")
            content = pattern[j:closing]
            charset = set()
            p = 0
            L = len(content)
            while p < L:
                if (p + 2 < L and content[p + 1] == '-'
                        and content[p] != '-' and content[p + 2] != '-'):
                    start = content[p]
                    end = content[p + 2]
                    if ord(start) <= ord(end):
                        for o in range(ord(start), ord(end) + 1):
                            charset.add(chr(o))
                    else:
                        # treat as literals rather than raising
                        charset.add(start)
                        charset.add('-')
                        charset.add(end)
                    p += 3
                else:
                    charset.add(content[p])
                    p += 1
            i = closing + 1
            quant = None
            if i < n and pattern[i] in ('*', '+', '?'):
                quant = pattern[i]
                i += 1
            tokens.append(('class', frozenset(charset), negate, quant))
        elif c == '.':
            i += 1
            quant = None
            if i < n and pattern[i] in ('*', '+', '?'):
                quant = pattern[i]
                i += 1
            tokens.append(('dot', None, None, quant))
        elif c == ']':
            # lone ']' outside class is a literal
            i += 1
            quant = None
            if i < n and pattern[i] in ('*', '+', '?'):
                quant = pattern[i]
                i += 1
            tokens.append(('lit', c, None, quant))
        else:
            # literal character (including '^', '$', '\\', '(', etc.)
            lit = c
            i += 1
            quant = None
            if i < n and pattern[i] in ('*', '+', '?'):
                quant = pattern[i]
                i += 1
            tokens.append(('lit', lit, None, quant))

    def single_match(kind, value, negate, ch):
        if kind == 'dot':
            return True
        if kind == 'lit':
            return ch == value
        # class
        if negate:
            return ch not in value
        else:
            return ch in value

    m = len(tokens)
    tlen = len(text)

    # memoization for (ti, si) -> bool to keep backtracking polynomial
    memo = {}

    import sys
    sys.setrecursionlimit(10000)

    def dfs(ti, si):
        key = (ti, si)
        if key in memo:
            return memo[key]
        if ti == m:
            res = (si == tlen)
            memo[key] = res
            return res
        kind, value, negate, quant = tokens[ti]
        if quant is None:
            if si >= tlen:
                memo[key] = False
                return False
            if not single_match(kind, value, negate, text[si]):
                memo[key] = False
                return False
            res = dfs(ti + 1, si + 1)
            memo[key] = res
            return res
        elif quant == '?':
            # try one then zero
            if si < tlen and single_match(kind, value, negate, text[si]):
                if dfs(ti + 1, si + 1):
                    memo[key] = True
                    return True
            res = dfs(ti + 1, si)
            memo[key] = res
            return res
        elif quant == '*':
            # compute max consecutive matches
            maxk = 0
            while si + maxk < tlen and single_match(kind, value, negate, text[si + maxk]):
                maxk += 1
            for k in range(maxk, -1, -1):
                if dfs(ti + 1, si + k):
                    memo[key] = True
                    return True
            memo[key] = False
            return False
        elif quant == '+':
            if si >= tlen or not single_match(kind, value, negate, text[si]):
                memo[key] = False
                return False
            maxk = 0
            while si + maxk < tlen and single_match(kind, value, negate, text[si + maxk]):
                maxk += 1
            for k in range(maxk, 0, -1):
                if dfs(ti + 1, si + k):
                    memo[key] = True
                    return True
            memo[key] = False
            return False
        else:
            memo[key] = False
            return False

    return dfs(0, 0)
