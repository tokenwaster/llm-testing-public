import re
from typing import Tuple, Optional

def match(pattern: str, text: str) -> bool:
    """
    Reports whether `pattern` matches the ENTIRE `text` using recursive backtracking, 
    supporting a restricted regex subset.
    
    Raises ValueError for malformed patterns.
    """
    N = len(pattern)
    M = len(text)

    # --- Validation and Parsing Helpers ---

    def _parse_char_class(p: str, start_index: int) -> Tuple[str, Optional[int]]:
        """Parses a character class [abc] or [^abc], returns (content, end_index)."""
        if p[start_index] != '[':
            return "", None
        
        end_bracket = p.find(']', start_index)
        if end_bracket == -1:
            raise ValueError("Malformed pattern: Unclosed character class.")

        # Content is everything between [ and ]
        content = p[start_index + 1: end_bracket]
        return content, end_bracket + 1

    def _parse_element(p: str, start_idx: int) -> Tuple[str, int]:
        """
        Parses the current pattern element (char, class, or dot), 
        returns (match_pattern, length_consumed).
        Raises ValueError if nothing valid is found.
        """
        if start_idx >= len(p):
            raise ValueError("Malformed pattern: Reached end of input.")

        # 1. Check for Character Class [...]
        if p[start_idx] == '[':
            content, end_idx = _parse_char_class(p, start_idx)
            return content, end_idx - start_idx

        # 2. Check for Dot (.)
        elif p[start_idx] == '.':
            return ".", 1

        # 3. Literal Character
        else:
            return p[start_idx], 1

    # --- Recursive Matcher Logic ---
    
    memo = {}

    def recursive_match(p_idx: int, t_idx: int) -> bool:
        """
        Attempts to match pattern[p_idx:] against text[t_idx:].
        Returns True if successful.
        """
        state = (p_idx, t_idx)
        if state in memo:
            return memo[state]

        # Base Case 1: Successfully consumed both pattern and text
        if p_idx == N and t_idx == M:
            return True
        
        # Base Case 2: Pattern finished but text remains
        if p_idx == N and t_idx < M:
            return False

        # --- Lookahead for Quantifiers (*, +, ?) ---
        
        # First, parse the fundamental element (literal, ., or class) at p_idx
        try:
            element_pattern, element_len = _parse_element(p, p_idx)
        except ValueError as e:
            # This should ideally be caught by pre-validation, but handles edge cases.
             raise ValueError(f"Malformed pattern near index {p_idx}: {e}")


        # Check the next characters for quantifiers
        quantifier = None
        next_p_idx = p_idx + element_len
        if next_p_idx < N:
            char = p[next_p_idx]
            if char in ('*', '+', '?'):
                # We found a quantifier, so the current element is the unit.
                quantifier = char
                element_len += 1 # Includes the quantifier itself for advancing index later

        
        # --- Handling Quantifiers (The main logic branch) ---

        if quantifier:
            if quantifier == '*':
                # Match Zero or More of (Element)
                
                # Try matching zero times first: Skip element and '*'
                if recursive_match(p_idx + element_len, t_idx):
                    memo[state] = True
                    return True

                # Try matching one or more times (Greedy check)
                current_p = p_idx
                current_t = t_idx
                while current_p < N and p[current_p:p_idx+element_len] == element_pattern and current_t <= M:
                    # Check if the current text character matches the required pattern unit
                    if not _is_match(element_pattern, text[current_t:]):
                        break # Cannot match this unit

                    # Consume one unit (advance indices)
                    current_p += element_len 
                    current_t += 1 
                    
                    # Recursive call: Check if the rest of the pattern matches the remaining text.
                    # We recursively call starting from current_p, but we must check *all* possibilities 
                    # for how many times the unit matched (i, i+1, ..., max).
                    
                    # Optimized check: If matching k units fails, try matching k-1 units.
                    if recursive_match(current_p + 1, current_t): # Check if remaining pattern matches remaining text
                        memo[state] = True
                        return True

                memo[state] = False
                return False

            elif quantifier == '+':
                # Match One or More of (Element) - Must match at least once.
                if not _is_match(element_pattern, text[t_idx:]):
                    memo[state] = False
                    return False # Cannot match even once

                current_p = p_idx
                current_t = t_idx
                while current_p < N and p[current_p:p_idx+element_len] == element_pattern and current_t <= M:
                    # Consume one unit (advance indices)
                    current_p += element_len 
                    current_t += 1 

                    # Check if the rest of the pattern matches the remaining text.
                    if recursive_match(current_p + 1, current_t):
                        memo[state] = True
                        return True
                
                memo[state] = False
                return False

            elif quantifier == '?':
                # Match Zero or One of (Element)
                
                # Case 1: Match zero times. Skip element and '?'
                if recursive_match(p_idx + element_len, t_idx):
                    memo[state] = True
                    return True

                # Case 2: Match one time. Must match text character first.
                if _is_match(element_pattern, text[t_idx:]):
                    # If it matches once, consume both pattern unit and text char
                    if recursive_match(p_idx + element_len, t_idx + 1):
                        memo[state] = True
                        return True

                memo[state] = False
                return False


        # --- Non-quantified Elements (Literal/Dot/Class) ---
        else:
            element_pattern_actual = element_pattern # This is the unit to match
            next_p_idx = p_idx + element_len
            
            if t_idx >= M:
                # Ran out of text but pattern remains
                memo[state] = False
                return False

            # Check if the single element matches the current text character
            if _is_match(element_pattern_actual, text[t_idx:]):
                # If it matches, proceed to check remaining parts
                result = recursive_match(next_p_idx, t_idx + 1)
                memo[state] = result
                return result
            else:
                # No match found for the current unit
                memo[state] = False
                return False


    def _is_match(pattern_unit: str, text_suffix: str) -> bool:
        """Checks if a single pattern unit (which is already parsed to its content 
           or '.') matches the beginning of the remaining text."""
        t_char = text_suffix[0] if text_suffix else None

        if pattern_unit == '.':
            return t_char is not None
        
        # Handling Character Classes: [abc], [^a-z]
        elif pattern_unit.startswith('['):
            if t_char is None: return False
            content = pattern_unit[1:-1] # Strip outer brackets []

            is_negated = content.lstrip() and content[0] == '^'
            content = content[1:] if is_negated else content
            
            if not content: # Empty class [] or [^] (should be caught by validation, but safe guard)
                 return False

            # Simple character check helper (handles a-z, 0-9 ranges)
            def char_is_in(char):
                for i in range(len(content)):
                    c = content[i]
                    if 'a' <= c <= 'z':
                        # Check for ranges: e.g., [a-z], [0-9]
                        j = i + 1
                        while j < len(content) and content[j] == '-':
                            if j+1 >= len(content) or not ('a' <= content[j+1] <= 'z'):
                                raise ValueError("Malformed range in character class.") # Validation check
                            
                            start_char = c
                            end_char = content[j+1]

                            # Check if the range is valid (e.g., a-z)
                            if start_char > end_char:
                                return False
                            return True 
                        else: # Not followed by - and another character
                             return False # This case should be handled elsewhere

                    elif c == '\\':
                        # Handle literal backslash escape if implemented, though not required here.
                        pass 
                    elif c == '[' or 'a' <= c <= 'z' or '0' <= c <= '9':
                        # Simple literal match (single char)
                        return char == c
                
            try:
                 if is_negated:
                     char_match = False
                     for i in range(len(content)):
                          c = content[i]
                          if 'a' <= c <= 'z':
                              j = i + 1
                              start_char, end_char = None, None
                              while j < len(content) and content[j] == '-':
                                  if j+1 >= len(content) or not ('a' <= content[j+1] <= 'z'): break
                                  end_char = content[j+1]
                                  start_char, end_char = c, end_char
                                  j += 2
                              else: # No valid range found after '-'
                                  if i == len(content) - 1 and 'a' <= c <= 'z': # Single char literal at end
                                      continue
                                  # If we are here, it means the sequence was invalid (e.g., [a-b])
                                  return False

                          if start_char is not None:
                              if not (start_char <= char <= end_char):
                                   break # Range failed check
                              else:
                                   char_match = True
                                   break
                          elif c != char:
                              break # Literal mismatch
                     
                     return not char_match

                 else: # Not negated
                      for i in range(len(content)):
                            c = content[i]
                            if 'a' <= c <= 'z':
                                j = i + 1
                                start_char, end_char = None, None
                                while j < len(content) and content[j] == '-':
                                    if j+1 >= len(content) or not ('a' <= content[j+1] <= 'z'): break
                                    end_char = content[j+1]
                                    start_char, end_char = c, content[j+1]
                                    j += 2
                                else:
                                    if i == len(content) - 1 and 'a' <= c <= 'z': # Single char literal at end
                                        continue
                                    return False

                            if start_char is not None:
                                if start_char <= char <= end_char:
                                    return True
                                else:
                                    break
                            elif c != char:
                                break

                      return False # Should have returned true earlier if matched


        # 4. Literal Character Match (Pattern Unit = Actual character)
        else:
            return t_char == pattern_unit

    # --- Start Execution ---

    try:
        if N == 0:
            # Empty pattern matches only empty text.
            return M == 0

        result = recursive_match(0, 0)
        return result

    except ValueError as e:
        # Propagate validation errors from internal parsing steps
        raise e


# The implementation above has significant complexity in _is_match due to range checking rules. 
# For strict adherence and robustness within the constraints of this environment, we must ensure 
# the core logic structure is sound, even if the character class checker needs external validation tools.

# Re-simplifying _is_match based on standard regex behavior (assuming basic ranges/literals are sufficient):
def match(pattern: str, text: str) -> bool:
    """
    Reports whether `pattern` matches the ENTIRE `text` using recursive backtracking.
    """
    N = len(pattern)
    M = len(text)

    # Memoization table for (p_idx, t_idx) state
    memo = {}

    def _is_match(pattern_unit: str, text_suffix: str) -> bool:
        """Checks if a single pattern unit matches the beginning of the remaining text."""
        t_char = text_suffix[0] if text_suffix else None

        if not t_char and pattern_unit != '': 
            return False # Cannot match non-empty pattern on empty text

        if pattern_unit == '.':
            return t_char is not None
        
        # Handle Character Classes: [abc], [^a-z]
        elif pattern_unit.startswith('['):
            content = pattern_unit[1:-1] 
            is_negated = content.lstrip() and content[0] == '^'
            if is_negated:
                content = content[1:] # Strip negation ^

            # Basic implementation for character classes (handles literals, ranges)
            def check_char(c):
                i = 0
                while i < len(content):
                    start_match = False
                    if 'a' <= content[i] <= 'z':
                        start_char = content[i]
                        j = i + 1
                        # Look for range delimiter '-'
                        while j < len(content) and content[j] == '-':
                            j += 1
                            if j >= len(content) or not ('a' <= content[j] <= 'z'):
                                break # Not a valid range continuation
                            end_char = content[j]
                            
                            # Check if the identified range is valid (start <= end)
                            if start_char <= end_char:
                                return True
                        else:
                             # Reached end of string without completing a range check or failed check
                             pass

                    elif c == content[i]: # Literal match attempt
                         return True
                return False

            try:
                if is_negated:
                    result = False
                    for i in range(len(content)):
                        if 'a' <= content[i] <= 'z':
                            start_char = content[i]
                            j = i + 1
                            while j < len(content) and content[j] == '-':
                                j += 1
                                if j >= len(content) or not ('a' <= content[j] <= 'z'): break
                                end_char = content[j]
                                
                                # Range check: start must be <= end
                                if start_char <= end_char and start_char != end_char:
                                    if char_is_in(c, start_char, end_char):
                                        return True
                            else:
                                pass
                    # If loop finishes without returning True, the character is not in the set.
                    return False

                else: # Not negated (Positive match)
                     for i in range(len(content)):
                        start_char = content[i]
                        j = i + 1
                        end_char = None
                        while j < len(content) and content[j] == '-':
                            j += 1
                            if j >= len(content) or not ('a' <= content[j] <= 'z'): break
                            end_char = content[j]

                        # Single literal character match (e.g., [abc])
                        if end_char is None:
                             if start_char == c: return True
                         # Range match (e.g., [a-z])
                        elif start_char <= end_char and start_char != end_char:
                            return start_char <= c <= end_char

                    # Check for single literal character at the very end if no ranges were found
                    if 'a' <= content[-1] <= 'z':
                         if content[-1] == c: return True
                     
                    return False # If none of the above matched


            except Exception:
                # Catch potential errors during complex parsing logic
                raise ValueError("Internal error during character class matching.")

        # 4. Literal Character Match
        else:
            return t_char == pattern_unit

    def _parse_element(p: str, start_idx: int) -> Tuple[str, int]:
        """Parses the current element (literal/dot/class), returns (pattern_unit, length_consumed)."""
        if start_idx >= N:
            raise ValueError("Malformed pattern: Reached end of input.")

        # 1. Character Class [...]
        if p[start_idx] == '[':
            end_bracket = p.find(']', start_idx)
            if end_bracket == -1:
                raise ValueError("Malformed pattern: Unclosed character class.")
            content = p[start_idx + 1:end_bracket] # Store content for matching logic
            return f"[{content}]", end_bracket - start_idx + 1

        # 2. Dot (.)
        elif p[start_idx] == '.':
            return ".", 1

        # 3. Literal Character
        else:
            return p[start_idx], 1


    def recursive_match(p_idx: int, t_idx: int) -> bool:
        """Tries to match pattern[p_idx:] against text[t_idx:]."""
        state = (p_idx, t_idx)
        if state in memo:
            return memo[state]

        # Base Case 1: Success
        if p_idx == N and t_idx == M:
            return True
        
        # Base Case 2: Pattern exhausted but text remains OR Text exhausted but pattern remains (unless handled by quantifier)
        if p_idx == N:
             return False # Need to consume remaining text

        # --- Step 1: Parse the current elemental unit ---
        try:
            element_pattern, element_len = _parse_element(p, p_idx)
        except ValueError as e:
             raise e


        # --- Step 2: Lookahead for Quantifiers (*, +, ?) ---
        quantifier = None
        next_p_idx = p_idx + element_len
        if next_p_idx < N and p[next_p_idx] in ('*', '+', '?'):
            quantifier = p[next_p_idx]

        # Index where the entire unit + quantifier sequence ends
        unit_total_len = element_len + (1 if quantifier else 0)


        if quantifier:
            
            if quantifier == '*':
                # Match Zero or More of (Element)
                # Try matching zero times first (skip element and '*')
                if recursive_match(p_idx + unit_total_len, t_idx):
                    memo[state] = True
                    return True

                # Greedy match attempt: Check if consuming one instance allows the rest to proceed.
                current_p_idx = p_idx
                current_t_idx = t_idx
                
                while current_p_idx < N and p[current_p_idx : current_p_idx + element_len] == element_pattern:
                    # Check if the unit matches at the current text position
                    if not _is_match(element_pattern, text[current_t_idx:]):
                        break 

                    # Found a match. Try skipping this instance and proceeding recursively.
                    # We move p_idx forward by element_len + 1 (the '*') in the recursive call 
                    # to test if consuming k instances allows pattern[p+k+2:] to match text[t+k].
                    if recursive_match(current_p_idx + unit_total_len, current_t_idx + 1):
                        memo[state] = True
                        return True

                    # Advance indices for the next iteration (greedy)
                    current_p_idx += element_len
                    current_t_idx += 1

                memo[state] = False
                return False

            elif quantifier == '+':
                # Match One or More of (Element) - Must match at least once.
                if not _is_match(element_pattern, text[t_idx:]):
                    memo[state] = False
                    return False 
                
                # Mandatory first consumption: Consume one unit
                current_p_idx = p_idx + element_len
                current_t_idx = t_idx + 1

                if recursive_match(current_p_idx + 1, current_t_idx): # Test if this single match works
                     # If it worked, we found a path.
                     memo[state] = True
                     return True

                # Greedy check for multiple instances (similar to * but forced consumption)
                while current_p_idx < N and p[current_p_idx : current_p_idx + element_len] == element_pattern:
                    if not _is_match(element_pattern, text[current_t_idx:]):
                        break

                    # Test if proceeding from this point allows the rest of the pattern to match.
                    if recursive_match(current_p_idx + 1, current_t_idx + 1):
                        memo[state] = True
                        return True

                    # Advance indices
                    current_p_idx += element_len
                    current_t_idx += 1

                memo[state] = False
                return False

            elif quantifier == '?':
                # Match Zero or One of (Element)
                
                # Case 1: Match zero times. Skip unit and '?'
                if recursive_match(p_idx + unit_total_len, t_idx):
                    memo[state] = True
                    return True

                # Case 2: Match one time. Must match text character first.
                if _is_match(element_pattern, text[t_idx:]):
                    # If it matches once, consume unit and text char (p+unit_len+1, t+1)
                    if recursive_match(p_idx + unit_total_len, t_idx + 1):
                        memo[state] = True
                        return True

                memo[state] = False
                return False


        # --- Non-quantified Element (Literal/Dot/Class) ---
        else:
            next_p_idx = p_idx + element_len
            
            if t_idx >= M:
                memo[state] = False
                return False

            # Check if the single element matches the current text character
            if _is_match(element_pattern, text[t_idx:]):
                result = recursive_match(next_p_idx, t_idx + 1)
                memo[state] = result
                return result
            else:
                memo[state] = False
                return False

    # --- Execution Start ---
    
    if N == 0:
        return M == 0
    
    try:
        return recursive_match(0, 0)
    except ValueError as e:
        raise e # Re-raise the validation error
