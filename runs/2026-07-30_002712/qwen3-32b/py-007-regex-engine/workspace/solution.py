def match(pattern: str, text: str) -> bool:
    # Validate basic pattern structure before starting matching
    i = 0
    while i < len(pattern):
        if pattern[i] in '*+?':
            if i == 0:
                raise ValueError("Malformed pattern")
            prev_char = pattern[i-1]
            if prev_char in '*+?':
                raise ValueError("Malformed pattern: consecutive quantifiers")
        i += 1

    def match_here(p_idx: int, t_idx: int) -> bool:
        # Base case: if pattern is exhausted
        if p_idx == len(pattern):
            return t_idx == len(text)

        current_char = pattern[p_idx]

        # Parse character class
        if current_char == '[':
            j = p_idx + 1
            if j >= len(pattern):
                raise ValueError("Unclosed [ in pattern")
            negated = False
            if pattern[j] == '^':
                negated = True
                j += 1
            end_j = None
            for k in range(j, len(pattern)):
                if pattern[k] == ']':
                    end_j = k
                    break
            if end_j is None:
                raise ValueError("Unclosed [ in pattern")
            allowed_chars = set()
            i_char_class = j  # Start parsing characters inside the class
            while i_char_class < end_j:
                c = pattern[i_char_class]
                if (i_char_class + 2 < end_j and 
                    pattern[i_char_class+1] == '-' and 
                    i_char_class+2 <= end_j):
                    start_char = c
                    end_char = pattern[i_char_class+2]
                    for ch in range(ord(start_char), ord(end_char) + 1):
                        allowed_chars.add(chr(ch))
                    i_char_class += 3
                else:
                    allowed_chars.add(c)
                    i_char_class += 1

            def char_matcher(text_char):
                if text_char is None:
                    return False
                if negated:
                    return text_char not in allowed_chars
                else:
                    return text_char in allowed_chars

            len_element = end_j - p_idx + 1
            next_pos = p_idx + len_element
            has_quantifier = (next_pos < len(pattern) and 
                              pattern[next_pos] in '*+?')
        elif current_char == '.':
            def dot_matcher(text_char):
                return text_char is not None

            len_element = 1
            next_pos = p_idx + 1
            has_quantifier = (next_pos < len(pattern) and 
                              pattern[next_pos] in '*+?')
        else:
            target_char = current_char
            def lit_matcher(text_char):
                return text_char == target_char

            len_element = 1
            next_pos = p_idx + 1
            has_quantifier = (next_pos < len(pattern) and 
                              pattern[next_pos] in '*+?')

        if not has_quantifier:
            # No quantifier: must match exactly once
            if t_idx >= len(text):
                return False

            text_char = text[t_idx]
            matched = False
            if current_char == '[':
                matched = char_matcher(text_char)
            elif current_char == '.':
                matched = dot_matcher(text_char)
            else:
                matched = lit_matcher(text_char)

            if not matched:
                return False

            # Move to next pattern and text positions
            return match_here(p_idx + len_element, t_idx + 1)
        else:
            quant_char = pattern[next_pos]
            if quant_char == '*':
                # Zero or more matches
                result_zero = match_here(next_pos + 1, t_idx)
                if result_zero:
                    return True

                if t_idx >= len(text):
                    return False
                text_char = text[t_idx]
                matched = False
                if current_char == '[':
                    matched = char_matcher(text_char)
                elif current_char == '.':
                    matched = dot_matcher(text_char)
                else:
                    matched = lit_matcher(text_char)

                if not matched:
                    return False

                # Consume character and retry with same element
                return match_here(p_idx, t_idx + 1)
            elif quant_char == '+':
                # One or more matches: must consume at least one
                if t_idx >= len(text):
                    return False
                text_char = text[t_idx]
                matched = False
                if current_char == '[':
                    matched = char_matcher(text_char)
                elif current_char == '.':
                    matched = dot_matcher(text_char)
                else:
                    matched = lit_matcher(text_char)

                if not matched:
                    return False

                option1 = match_here(next_pos + 1, t_idx + 1)
                option2 = match_here(p_idx, t_idx + 1)
                return option1 or option2
            elif quant_char == '?':
                # Zero or one match
                result_zero = match_here(next_pos + 1, t_idx)
                if result_zero:
                    return True

                if t_idx >= len(text):
                    return False
                text_char = text[t_idx]
                matched = False
                if current_char == '[':
                    matched = char_matcher(text_char)
                elif current_char == '.':
                    matched = dot_matcher(text_char)
                else:
                    matched = lit_matcher(text_char)

                if not matched:
                    return False

                # Consume character and proceed with rest after quantifier
                return match_here(next_pos + 1, t_idx + 1)
            else:
                raise ValueError("Invalid quantifier")

    try:
        return match_here(0, 0)
    except ValueError as e:
        raise e
