def match(pattern: str, text: str) -> bool:
    def parse_pattern(p: str):
        elements = []
        i = 0
        n = len(p)
        while i < n:
            c = p[i]
            if c in '*+?':
                raise ValueError("quantifier with nothing before it")
            if c == '.':
                i += 1
                quant = ''
                if i < n and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                elements.append(('dot', None, quant))
            elif c == '[':
                i += 1
                if i >= n:
                    raise ValueError("unclosed [")
                negated = False
                if p[i] == '^':
                    negated = True
                    i += 1
                start = i
                while i < n and p[i] != ']':
                    i += 1
                if i >= n:
                    raise ValueError("unclosed [")
                class_content = p[start:i]
                i += 1  # skip ']'
                # parse class_content
                chars_set = set()
                j = 0
                clen = len(class_content)
                while j < clen:
                    if j + 2 < clen and class_content[j+1] == '-':
                        start_c = class_content[j]
                        end_c = class_content[j+2]
                        if ord(start_c) > ord(end_c):
                            raise ValueError("invalid range in character class")
                        for code in range(ord(start_c), ord(end_c)+1):
                            chars_set.add(chr(code))
                        j += 3
                    else:
                        chars_set.add(class_content[j])
                        j += 1
                if not chars_set:
                    raise ValueError("empty character class")
                quant = ''
                if i < n and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                elements.append(('class', (chars_set, negated), quant))
            else:
                # literal character
                ch = c
                i += 1
                quant = ''
                if i < n and p[i] in '*+?':
                    quant = p[i]
                    i += 1
                elements.append(('char', ch, quant))
        return elements

    def matches_element(elem, ch):
        typ, val = elem
        if typ == 'char':
            return ch == val
        elif typ == 'dot':
            return True
        elif typ == 'class':
            chars_set, negated = val
            if negated:
                return ch not in chars_set
            else:
                return ch in chars_set
        return False

    elements = parse_pattern(pattern)
    memo = {}

    def dfs(e_idx, t_idx):
        key = (e_idx, t_idx)
        if key in memo:
            return memo[key]
        if e_idx == len(elements):
            result = (t_idx == len(text))
            memo[key] = result
            return result
        typ, val, quant = elements[e_idx]
        elem = (typ, val)
        if quant == '':
            if t_idx < len(text) and matches_element(elem, text[t_idx]):
                result = dfs(e_idx + 1, t_idx + 1)
            else:
                result = False
        elif quant == '?':
            if dfs(e_idx + 1, t_idx):
                result = True
            elif t_idx < len(text) and matches_element(elem, text[t_idx]):
                result = dfs(e_idx + 1, t_idx + 1)
            else:
                result = False
        elif quant == '*':
            if dfs(e_idx + 1, t_idx):
                result = True
            elif t_idx < len(text) and matches_element(elem, text[t_idx]):
                result = dfs(e_idx, t_idx + 1) or dfs(e_idx + 1, t_idx + 1)
            else:
                result = False
        elif quant == '+':
            if t_idx < len(text) and matches_element(elem, text[t_idx]):
                result = dfs(e_idx, t_idx + 1) or dfs(e_idx + 1, t_idx + 1)
            else:
                result = False
        else:
            result = False
        memo[key] = result
        return result

    return dfs(0, 0)
