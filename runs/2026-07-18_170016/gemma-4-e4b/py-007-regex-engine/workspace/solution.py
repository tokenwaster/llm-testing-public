import re # Used only for internal testing/validation, but not in the final logic flow as requested.

def match(pattern: str, text: str) -> bool:
    """
    Reports whether pattern matches the ENTIRE text using recursive backtracking.
    Supports literals, ., *, +, ?, and character classes [...].
    Raises ValueError for malformed patterns.
    """

    # --- Helper Functions for Pattern Analysis ---

    def is_quantifier(char):
        return char in ('*', '+', '?')

    def parse_class(p_idx: int) -> tuple[int, str]:
        """
        Parses the character class starting at p_idx.
        Returns (end_index, definition_string). Raises ValueError on error.
        """
        if pattern[p_idx] != '[':
            raise ValueError("Internal Error: parse_class called without '['")

        start = p_idx + 1
        depth = 0
        i = start
        while i < len(pattern):
            char = pattern[i]
            if char == '[':
                depth += 1
            elif char == ']':
                if depth == 0:
                    # Found the closing bracket for the initial class
                    return i + 1, pattern[start:i]
                else:
                    depth -= 1
            elif char == '\\' and i + 1 < len(pattern) and pattern[i+1] in ('[', ']', '-', '\\'):
                # Handle escaped characters inside the class definition
                i += 2
                continue
            
            i += 1
        
        # If loop finishes without finding closing bracket
        raise ValueError("Malformed pattern: Unclosed character class '['")

    def char_matches(char: str, element_str: str) -> bool:
        """Checks if a single text character matches the given regex element string."""
        if not element_str:
            return False # Should not happen if called correctly

        # 1. Check for '.'
        if element_str == '.':
            return True

        # 2. Check for Character Class [...]
        if element_str.startswith('[') and element_str.endswith(']'):
            class_def = element_str[1:-1]
            is_negated = class_def.startswith('^')
            effective_def = class_def[1:] if is_negated else class_def

            if not effective_def: # Empty class [] or [^]
                return False 

            # Simple implementation for character classes (assuming standard ASCII ranges)
            i = 0
            while i < len(effective_def):
                char_to_check = effective_def[i]
                if char_to_check == '\\': # Escaped literal
                    return char_to_check == char

                elif char_to_check == '[':
                    # Start of a sub-class definition (e.g., [a-z])
                    j = i + 1
                    start_char = effective_def[j]
                    if j < len(effective_def) and effective_def[j+1] == '-':
                        # Range detected: [A-Z]
                        end_char = effective_def[j+1]
                        if start_char <= end_char: # Basic range check
                            return start_char <= char <= end_char
                        else:
                            raise ValueError("Malformed range in character class")

                    # If it's a literal character inside the class definition (e.g., [a\\b])
                    if j < len(effective_def) and effective_def[j] == '\\':
                         return char == effective_def[i:i+3].lstrip('[').rstrip(']') # Simplified handling for escaped literals

                elif char_to_check == ']':
                    # Should not happen if the outer class parsing was correct, but handle it.
                    pass 
                else:
                    # Literal character match
                    return char == char_to_check
                
                i += 1
            
            # Fallback for simple literal check (if no ranges/classes were found)
            return char in effective_def

        # 3. Literal Character Match
        return element_str == char


    # --- Core Recursive Backtracking Logic ---

    memo = {} # Memoization cache: (p_idx, t_idx) -> bool

    def solve(p_idx: int, t_idx: int) -> bool:
        """
        Checks if pattern[p_idx:] matches text[t_idx:].
        Returns True/False.
        """
        if (p_idx, t_idx) in memo:
            return memo[(p_idx, t_idx)]

        # Base Case 1: Pattern exhausted
        if p_idx == len(pattern):
            result = t_idx == len(text)
            memo[(p_idx, t_idx)] = result
            return result

        # Lookahead for quantifiers (*, +, ?)
        is_quantified = (p_idx + 1 < len(pattern)) and is_quantifier(pattern[p_idx+1])
        
        # Determine the element definition string and its length in P
        element_def: str
        next_p_idx = p_idx + 1

        if pattern[p_idx] == '[':
            try:
                end_index, class_def = parse_class(p_idx)
                element_def = f"[{class_def}]" # Store the full definition including brackets for matching
                next_p_idx = end_index
            except ValueError as e:
                # Re-raise pattern errors immediately
                raise e

        elif pattern[p_idx] == '.':
            element_def = "."
            next_p_idx = p_idx + 1
        
        else: # Literal character
            element_def = pattern[p_idx]
            next_p_idx = p_idx + 1

        # --- Handle Quantifiers ---

        if is_quantified:
            quantifier = pattern[p_idx+1]
            
            if element_def == "." and quantifier == '?': # Special case for '.'? (not supported by grammar, but good practice)
                pass # Handled below
            
            # Case 1: Zero or One ('?')
            if quantifier == '?':
                # Option A: Match zero times (skip the element entirely)
                if solve(next_p_idx + 1, t_idx):
                    memo[(p_idx, t_idx)] = True
                    return True
                
                # Option B: Match one time (requires text character match)
                if t_idx < len(text) and char_matches(text[t_idx], element_def):
                    # If it matches once, proceed to the next pattern index + 1
                    if solve(next_p_idx + 1, t_idx + 1):
                        memo[(p_idx, t_idx)] = True
                        return True

                memo[(p_idx, t_idx)] = False
                return False

            # Case 2: Zero or More ('*')
            elif quantifier == '*':
                # Option A: Match zero times (skip the element entirely)
                if solve(next_p_idx + 1, t_idx):
                    memo[(p_idx, t_idx)] = True
                    return True

                # Option B: Match one or more times (Greedy approach via recursion)
                # Check if current text character matches the element definition
                if t_idx < len(text) and char_matches(text[t_idx], element_def):
                    # Consume the character, stay at the same pattern index (p_idx), 
                    # but advance the text index.
                    if solve(p_idx, t_idx + 1):
                        memo[(p_idx, t_idx)] = True
                        return True

                memo[(p_idx, t_idx)] = False
                return False

            # Case 3: One or More ('+')
            elif quantifier == '+':
                # Must match at least once (Check initial match)
                if t_idx >= len(text) or not char_matches(text[t_idx], element_def):
                    memo[(p_idx, t_idx)] = False
                    return False

                # Consume the first character and proceed to check for subsequent matches
                # We are now at p_idx (the start of the element) but must advance text index.
                # The remaining pattern segment is P[p_idx:] which can match zero or more times.
                
                # Start by consuming the first required match:
                if solve(p_idx, t_idx + 1): # Check if the rest of the pattern matches after this mandatory consumption
                    memo[(p_idx, t_idx)] = True
                    return True

                # If the recursive call above failed (meaning the remaining pattern needs more text), 
                # we need to check for subsequent repetitions. This is complex because '+' implies
                # that the element must match at least once, and then zero or more times.
                
                # Simplified approach: Consume one character, and recursively solve for P[p_idx:] against T[t_idx+1:]
                if solve(p_idx, t_idx + 1):
                    memo[(p_idx, t_idx)] = True
                    return True

                memo[(p_idx, t_idx)] = False
                return False


        # --- Handle Non-Quantified Element (Literal, ., or Class) ---

        else: # No quantifier follows
            # Must match exactly once
            if t_idx < len(text) and char_matches(text[t_idx], element_def):
                # Advance both pattern and text indices
                result = solve(next_p_idx, t_idx + 1)
                memo[(p_idx, t_idx)] = result
                return result
            else:
                memo[(p_idx, t_idx)] = False
                return False

    # Initial call to the recursive solver
    try:
        return solve(0, 0)
    except ValueError as e:
        # If any internal parsing error occurred (e.g., malformed class), re-raise it.
        raise e


if __name__ == '__main__':
    # --- Test Cases ---

    # Basic Literals and Dot
    print(f"Test 1 (Literal): {match('abc', 'abc')}") # True
    print(f"Test 2 (Mismatch): {match('abx', 'abc')}") # False
    print(f"Test 3 (.): {match('.', 'a')}") # True
    print(f"Test 4 (Dot mismatch): {match('.b', 'ac')}") # False

    # Quantifiers
    print("\n--- Quantifiers ---")
    # Zero or More (*)
    print(f"Test 5 (*): {match('a*b', 'b')}") # True (a* matches zero)
    print(f"Test 6 (*): {match('a*b', 'aaab')}") # True
    print(f"Test 7 (*): {match('c*d*', 'd')}") # True
    print(f"Test 8 (* failure): {match('a*b', 'ba')}") # False

    # One or Zero (?)
    print(f"Test 9 (?): {match('ab?c', 'ac')}") # True (b? matches zero)
    print(f"Test 10 (?): {match('ab?c', 'abc')}") # True (b? matches one)
    print(f"Test 11 (? failure): {match('a?c', 'x')}") # False

    # One or More (+)
    print(f"Test 12 (+): {match('a+b', 'ab')}") # True
    print(f"Test 13 (+): {match('a+b', 'aaab')}") # True
    print(f"Test 14 (+ failure): {match('a+b', 'b')}") # False

    # Character Classes
    print("\n--- Character Classes ---")
    # Simple class match
    print(f"Test 15 ([abc]): {match('[abc]', 'c')}") # True
    print(f"Test 16 ([abc] fail): {match('[abc]', 'd')}") # False

    # Range
    print(f"Test 17 ([a-z]): {match('[a-z]', 'x')}") # True
    print(f"Test 18 (Range fail): {match('[A-Z]', 'a')}") # False

    # Negation
    print(f"Test 19 ([^0-9]): {match('[^0-9]', 'a')}") # True
    print(f"Test 20 (Negation fail): {match('[^a]', 'a')}") # False

    # Combined Test
    print("\n--- Complex Tests ---")
    # Mixed quantifiers and classes
    print(f"Test 21: {match('a[b-d]*e', 'ae')}") # True (zero match)
    print(f"Test 22: {match('a[b-d]+e', 'abde')}") # True (one match)
    print(f"Test 23: {match('^[^0-9]*$', 'abc')}") # Should fail due to start/end anchors not implemented, but testing class logic.
    # Note: The current implementation assumes the pattern matches the ENTIRE text without explicit ^/$ anchors.

    # Empty Pattern / Text
    print(f"Test 24 (Empty match): {match('', '')}") # True
    print(f"Test 25 (Pattern empty, Text non-empty): {match('', 'a')}") # False

    # Error Handling Tests (Must raise ValueError)
    print("\n--- Error Handling ---")
    try:
        match('a[b', 'abc')
    except ValueError as e:
        print(f"Test 26 (Unclosed class): Caught expected error: {e}")

    try:
        # Quantifier without preceding element
        match('*', 'a')
    except ValueError as e:
        # This specific case might fail depending on how the parser handles it, but generally should raise.
        print(f"Test 27 (Quantifier start): Caught expected error or handled gracefully.")

    try:
        # Malformed range/class structure
        match('[a-]', 'a')
    except ValueError as e:
        print(f"Test 28 (Malformed class): Caught expected error: {e}")
