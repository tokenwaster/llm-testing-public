def match(pattern: str, text: str) -> bool:
    if not pattern:
        return not text

    def parse_pattern():
        tokens = []
        i = 0
        n = len(pattern)
        while i < n:
            if pattern[i] == '[':
                j = i + 1
                escaped = False
                while j < n:
                    c = pattern[j]
                    if not escaped and c == '\\':
                        escaped = True
                        j += 1
                    elif not escaped and c == ']':
                        break
                    else:
                        escaped = False
                        j += 1
                if j >= n:
                    raise ValueError("Unclosed [...] in pattern")
                class_str = pattern[i:j+1]
                inner = class_str[1:-1]
                negate = False
                if inner.startswith('^'):
                    negate = True
                    inner = inner[1:]
                allowed_chars = set()
                k = 0
                while k < len(inner):
                    if k + 2 < len(inner) and inner[k+1] == '-':
                        start_char = inner[k]
                        end_char = inner[k+2]
                        for c in range(ord(start_char), ord(end_char)+1):
                            allowed_chars.add(chr(c))
                        k += 3
                    else:
                        allowed_chars.add(inner[k])
                        k += 1
                tokens.append(('class', (allowed_chars, negate), None))
                i = j + 1

                if i < n and pattern[i] in "*+?":
                    modifier = pattern[i]
                    i += 1
                    prev_token = tokens[-1]
                    tokens[-1] = ('class', (allowed_chars, negate), modifier)
            else:
                current_char = pattern[i]
                if current_char in "*+?":
                    raise ValueError(f"Invalid pattern: {current_char} must follow an element")
                token_type = 'literal' if current_char != '.' else 'dot'
                base_value = current_char if token_type == 'literal' else None
                tokens.append((token_type, base_value, None))
                i += 1

                if i < n and pattern[i] in "*+?":
                    modifier = pattern[i]
                    i += 1
                    prev_token = tokens[-1]
                    tokens[-1] = (prev_token[0], prev_token[1], modifier)
        return tokens

    try:
        tokens = parse_pattern()
    except ValueError as e:
        raise e

    def matches_base(token_type, base_value, char):
        if token_type == 'literal':
            return base_value == char
        elif token_type == 'dot':
            return True
        elif token_type == 'class':
            allowed_chars, negate = base_value
            return (char in allowed_chars) != negate

    def match_here(token_index, text_pos):
        if token_index == len(tokens):
            return text_pos == len(text)

        current_token_type, base_value, modifier = tokens[token_index]

        if modifier is None:
            if text_pos >= len(text):
                return False
            if not matches_base(current_token_type, base_value, text[text_pos]):
                return False
            return match_here(token_index + 1, text_pos + 1)
        elif modifier == '*':
            if match_here(token_index + 1, text_pos):
                return True
            if text_pos < len(text) and matches_base(current_token_type, base_value, text[text_pos]):
                return match_here(token_index, text_pos + 1)
            else:
                return False
        elif modifier == '+':
            if text_pos >= len(text):
                return False
            if not matches_base(current_token_type, base_value, text[text_pos]):
                return False
            return match_here(token_index + 1, text_pos + 1) or \
                   match_here(token_index, text_pos + 1)
        elif modifier == '?':
            if match_here(token_index + 1, text_pos):
                return True
            if text_pos < len(text) and matches_base(current_token_type, base_value, text[text_pos]):
                return match_here(token_index + 1, text_pos + 1)
            else:
                return False

    return match_here(0, 0)
