def match(pattern: str, text: str) -> bool:
    # Parse pattern into a list of (element, quantifier) pairs.
    atoms = []
    i = 0
    n = len(pattern)
    while i < n:
        ch = pattern[i]
        if ch == '[':
            i += 1
            if i >= n:
                raise ValueError("unclosed [")
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
            start_i = i
            while i < n and pattern[i] != ']':
                i += 1
            if i >= n:
                raise ValueError("unclosed [")
            class_content = pattern[start_i:i]
            i += 1  # skip ']'
            if not class_content:
                raise ValueError("empty character class")
            ranges = []
            j = 0
            clen = len(class_content)
            while j < clen:
                if j + 2 < clen and class_content[j+1] == '-':
                    start_c = class_content[j]
                    end_c = class_content[j+2]
                    if ord(start_c) > ord(end_c):
                        raise ValueError(f"invalid range {start_c}-{end_c}")
                    ranges.append((ord(start_c), ord(end_c)))
                    j += 3
                else:
                    ranges.append((ord(class_content[j]), ord(class_content[j])))
                    j += 1
            elem = ('class', ranges, negated)
        elif ch == '.':
            elem = ('dot',)
            i += 1
        elif ch in '*+?':
            raise ValueError(f"quantifier {ch} with nothing before it")
        else:
            elem = ('char', ch)
            i += 1

        quant = None
        if i < n and pattern[i] in '*+?':
            quant = pattern[i]
            i += 1
        atoms.append((elem, quant))

    # Memoized recursive matcher.
    memo = {}

    def elem_match(elem, ch):
        typ = elem[0]
        if typ == 'char':
            return ch == elem[1]
        if typ == 'dot':
            return True
        if typ == 'class':
            _, ranges, negated = elem
            code = ord(ch)
            matched = any(start <= code <= end for start, end in ranges)
            return not matched if negated else matched
        return False

    def dp(a_idx, t_idx):
        key = (a_idx, t_idx)
        if key in memo:
            return memo[key]
        if a_idx == len(atoms):
            result = (t_idx == len(text))
            memo[key] = result
            return result
        elem, quant = atoms[a_idx]
        if quant == '*':
            min_rep = 0
            max_rep = len(text) - t_idx
        elif quant == '+':
            min_rep = 1
            max_rep = len(text) - t_idx
        elif quant == '?':
            min_rep = 0
            max_rep = 1
        else:
            min_rep = 1
            max_rep = 1

        # Try zero repetitions if allowed.
        if min_rep == 0:
            if dp(a_idx + 1, t_idx):
                memo[key] = True
                return True

        # Try 1 .. max_rep repetitions.
        for k in range(1, max_rep + 1):
            if t_idx + k - 1 >= len(text):
                break
            if not elem_match(elem, text[t_idx + k - 1]):
                break
            if k >= min_rep:
                if dp(a_idx + 1, t_idx + k):
                    memo[key] = True
                    return True

        memo[key] = False
        return False

    return dp(0, 0)
