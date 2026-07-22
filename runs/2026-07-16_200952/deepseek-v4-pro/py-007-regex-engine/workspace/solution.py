def match(pattern: str, text: str) -> bool:
    """
    Returns True if pattern matches the entire text using the supported regex subset.
    Raises ValueError for malformed patterns.
    """

    # ---------- parse pattern into list of nodes ----------
    nodes = []
    i = 0
    n = len(pattern)

    while i < n:
        c = pattern[i]

        # A quantifier at the very beginning of an element is an error
        if c in ('*', '+', '?'):
            raise ValueError("unexpected quantifier")

        if c == '.':
            nodes.append(('dot', None, ''))   # kind, data, quantifier
            i += 1

        elif c == '[':
            # find closing ']'
            j = i + 1
            while j < n and pattern[j] != ']':
                j += 1
            if j == n:
                raise ValueError("unclosed '['")
            inner = pattern[i+1:j]
            negate = False
            if inner.startswith('^'):
                negate = True
                inner = inner[1:]

            charset = set()
            k = 0
            while k < len(inner):
                ch = inner[k]
                # range like a-z, 0-9
                if (k + 1 < len(inner) and inner[k+1] == '-'
                        and k + 2 < len(inner)):
                    start = ch
                    end = inner[k+2]
                    for code in range(ord(start), ord(end) + 1):
                        charset.add(chr(code))
                    k += 3
                else:
                    charset.add(ch)
                    k += 1

            nodes.append(('class', (negate, charset), ''))
            i = j + 1

        else:
            # literal character (special regex characters outside a class lose their meaning here)
            nodes.append(('lit', c, ''))
            i += 1

        # after an element, maybe a quantifier appears
        if i < n and pattern[i] in ('*', '+', '?'):
            last = nodes[-1]
            if last[2] != '':
                raise ValueError("multiple quantifiers")
            nodes[-1] = (last[0], last[1], pattern[i])
            i += 1

    # ---------- recursive backtracking matcher ----------
    def match_nodes(pi: int, ti: int) -> bool:
        if pi == len(nodes):
            # all pattern nodes consumed: must also be at end of text
            return ti == len(text)

        node = nodes[pi]
        kind, data, quant = node

        def matches(ch: str) -> bool:
            if kind == 'lit':
                return ch == data
            if kind == 'dot':
                return True
            # kind == 'class'
            negate, charset = data
            return (ch in charset) != negate

        if quant == '':
            if ti < len(text) and matches(text[ti]):
                return match_nodes(pi + 1, ti + 1)
            return False

        if quant == '?':
            # try zero
            if match_nodes(pi + 1, ti):
                return True
            # try one
            if ti < len(text) and matches(text[ti]):
                if match_nodes(pi + 1, ti + 1):
                    return True
            return False

        if quant == '*':
            # zero first
            if match_nodes(pi + 1, ti):
                return True
            # then try one or more (non‑greedy backtracking)
            k = ti
            while k < len(text) and matches(text[k]):
                k += 1
                if match_nodes(pi + 1, k):
                    return True
            return False

        if quant == '+':
            # at least one
            if ti >= len(text):
                return False
            k = ti
            while k < len(text) and matches(text[k]):
                k += 1
                if match_nodes(pi + 1, k):
                    return True
            return False

        # should never be reached
        return False

    # ---------- start matching ----------
    return match_nodes(0, 0)
