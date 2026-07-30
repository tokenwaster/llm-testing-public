class PatternElement:
    """Base class for pattern elements."""
    pass

class LiteralElement(PatternElement):
    def __init__(self, char):
        self.char = char
    
    def match(self, text, pos):
        if pos < len(text) and text[pos] == self.char:
            return [(pos + 1, True)]
        return []

class AnyElement(PatternElement):
    """Matches any single character."""
    def match(self, text, pos):
        if pos < len(text):
            return [(pos + 1, True)]
        return []

class CharClassElement(PatternElement):
    def __init__(self, chars_set):
        self.chars_set = chars_set
    
    def match(self, text, pos):
        if pos < len(text) and text[pos] in self.chars_set:
            return [(pos + 1, True)]
        return []

class QuantifiedElement(PatternElement):
    """Wraps an element with a quantifier."""
    def __init__(self, element, quantifier):
        self.element = element
        self.quantifier = quantifier  # None, '*', '+', or '?'
    
    def match(self, text, pos):
        results = []
        
        if self.quantifier is None:
            return self.element.match(text, pos)
        
        elif self.quantifier == '*':
            # Zero or more matches - try all possible counts
            for count in range(len(text) - pos + 1):
                new_pos = pos
                matched_all = True
                
                # Try to match 'count' occurrences
                temp_pos = pos
                actual_count = 0
                while actual_count < count and temp_pos < len(text):
                    sub_results = self.element.match(text, temp_pos)
                    if not sub_results:
                        matched_all = False
                        break
                    temp_pos = sub_results[0][0]
                    actual_count += 1
                
                if matched_all and actual_count == count:
                    # Now try to match the rest of the pattern starting at new_pos
                    results.append((temp_pos, True))
        
        elif self.quantifier == '+':
            # One or more matches - need at least one match first
            for min_count in range(1, len(text) - pos + 2):  # Try different counts starting from 1
                temp_pos = pos
                matched_all = True
                
                for _ in range(min_count):
                    sub_results = self.element.match(text, temp_pos)
                    if not sub_results:
                        matched_all = False
                        break
                    temp_pos = sub_results[0][0]
                
                if matched_all and temp_pos > pos:  # Must have at least one match
                    results.append((temp_pos, True))
        
        elif self.quantifier == '?':
            # Zero or one match - try both possibilities
            # First, try zero matches (just continue)
            results.append((pos, True))
            
            # Then, try one match if possible
            sub_results = self.element.match(text, pos)
            for new_pos, _ in sub_results:
                results.append((new_pos, True))
        
        return results

def parse_pattern(pattern):
    """Parse the pattern into a list of PatternElement objects."""
    elements = []
    i = 0
    
    while i < len(pattern):
        element = None
        quantifier = None
        
        # Check for character class
        if pattern[i] == '[':
            i += 1
            if i >= len(pattern):
                raise ValueError("Unclosed character class")
            
            # Check for negation
            negated = False
            if pattern[i] == '^':
                negated = True
                i += 1
            
            chars_set = set()
            
            while i < len(pattern) and pattern[i] != ']':
                # Check for range like a-z
                if (i + 2 < len(pattern) and 
                    pattern[i+1] == '-' and 
                    pattern[i+2] != ']'):
                    start_char = pattern[i]
                    end_char = pattern[i+2]
                    if ord(start_char) > ord(end_char):
                        raise ValueError(f"Invalid character range {start_char}-{end_char}")
                    for c in range(ord(start_char), ord(end_char) + 1):
                        chars_set.add(chr(c))
                    i += 3
                else:
                    # Single character
                    chars_set.add(pattern[i])
                    i += 1
            
            if i >= len(pattern):
                raise ValueError("Unclosed character class")
            
            i += 1  # Skip the ']'
            
            if negated:
                # Create a set of all characters except those in chars_set
                all_chars = set(chr(c) for c in range(256))  # Extended ASCII
                chars_set = all_chars - chars_set
            
            element = CharClassElement(chars_set)
        
        elif pattern[i] == '.':
            element = AnyElement()
            i += 1
        
        else:
            # Literal character
            element = LiteralElement(pattern[i])
            i += 1
        
        # Check for quantifier
        if i < len(pattern) and pattern[i] in '*+?':
            quantifier = pattern[i]
            i += 1
        
        elements.append(QuantifiedElement(element, quantifier))
    
    return elements

def match_element(elements, text, pos):
    """Try to match the remaining elements starting at position pos."""
    if not elements:
        # No more elements to match - check if we've consumed all text
        return pos == len(text)
    
    element = elements[0]
    rest = elements[1:]
    
    results = element.match(text, pos)
    
    for new_pos, _ in results:
        if match_element(rest, text, new_pos):
            return True
    
    return False

def match(pattern, text):
    """Check if the entire text matches the pattern."""
    # Handle empty pattern case
    if not pattern:
        return len(text) == 0
    
    try:
        elements = parse_pattern(pattern)
        return match_element(elements, text, 0)
    except IndexError:
        raise ValueError("Malformed pattern")

# Additional validation for malformed patterns during parsing
def validate_and_match(pattern, text):
    """Validate pattern and check if it matches the entire text."""
    if not pattern:
        return len(text) == 0
    
    # Validate quantifiers at start
    i = 0
    while i < len(pattern):
        if pattern[i] in '*+?':
            raise ValueError(f"Invalid quantifier '{pattern[i]}' with nothing before it")
        if pattern[i] == '[':
            # Skip character class content for validation
            i += 1
            found_close = False
            while i < len(pattern):
                if pattern[i] == ']':
                    found_close = True
                    i += 1
                    break
                if (pattern[i] == '-' and i + 2 < len(pattern) and 
                    pattern[i+1].isalpha() and pattern[i+2] != ']'):
                    i += 3
                elif pattern[i:i+3] in ['[a', '[b', '[c']:  # Simple heuristic for ranges
                    i += 3
                else:
                    i += 1
            if not found_close:
                raise ValueError("Unclosed character class")
        else:
            i += 1
    
    # Now do the actual matching with backtracking
    def backtrack(elements, pos):
        if not elements:
            return pos == len(text)
        
        elem = elements[0]
        rest = elements[1:]
        
        for new_pos in get_match_positions(elem, text, pos):
            if backtrack(rest, new_pos):
                return True
        
        return False
    
    def get_match_positions(elem, text, pos):
        """Get all possible positions after matching an element."""
        results = []
        
        # Determine what the base element matches
        if isinstance(elem, LiteralElement):
            base_char = elem.char
            if pos < len(text) and text[pos] == base_char:
                results.append(pos + 1)
        
        elif isinstance(elem, AnyElement):
            if pos < len(text):
                results.append(pos + 1)
        
        elif hasattr(elem, 'chars_set'):  # CharClassElement
            if pos < len(text) and text[pos] in elem.chars_set:
                results.append(pos + 1)
        
        else:  # QuantifiedElement or unknown
            base = elem.element if hasattr(elem, 'element') else elem
            
            quant = elem.quantifier if hasattr(elem, 'quantifier') else None
            
            if quant is None:
                for p in get_match_positions(base, text, pos):
                    results.append(p)
            
            elif quant == '*':
                # Zero or more
                results.append(pos)  # Zero matches
                temp = pos
                while True:
                    sub_results = get_match_positions(base, text, temp)
                    if not sub_results:
                        break
                    for new_pos in sub_results:
                        results.append(new_pos)
                    if len(sub_results) == 1 and sub_results[0] == temp + 1:
                        temp = sub_results[0]
                    else:
                        break
            
            elif quant == '+':
                # One or more
                first_match = get_match_positions(base, text, pos)
                for new_pos in first_match:
                    results.append(new_pos)
                    temp = new_pos
                    while True:
                        more = get_match_positions(base, text, temp)
                        if not more:
                            break
                        for p in more:
                            results.append(p)
                        if len(more) == 1 and more[0] > temp:
                            temp = more[0]
                        else:
                            break
            
            elif quant == '?':
                # Zero or one
                results.append(pos)  # Zero matches
                for p in get_match_positions(base, text, pos):
                    results.append(p)  # One match
        
        return sorted(set(results)) if results else []
    
    try:
        elements = parse_pattern(pattern)
        return backtrack(elements, 0)
    except (ValueError, IndexError):
        raise ValueError("Malformed pattern")

# Main matching function using the working implementation
def match(pattern: str, text: str) -> bool:
    """Check if the entire text matches the pattern."""
    
    # Handle empty pattern case
    if not pattern:
        return len(text) == 0
    
    def parse_chars_class(s, i):
        """Parse a character class starting at position i (after '[')."""
        negated = False
        chars_set = set()
        
        # Check for negation
        if s[i] == '^':
            negated = True
            i += 1
        
        start_i = i
        while i < len(s) and s[i] != ']':
            # Check for range like a-z or 0-9
            if (i + 2 < len(s) and s[i+1] == '-' and s[i+2] != ']'):
                start_char = s[i]
                end_char = s[i+2]
                
                # Validate range is valid (start <= end)
                if ord(start_char) > ord(end_char):
                    raise ValueError(f"Invalid character range: {start_char}-{end_char}")
                
                for c in range(ord(start_char), ord(end_char) + 1):
                    chars_set.add(chr(c))
                i += 3
            else:
                # Single character
                chars_set.add(s[i])
                i += 1
        
        if i >= len(s):
            raise ValueError("Unclosed character class")
        
        return chars_set, negated, i + 1  # Return position after ']'
    
    def match_recursive(pattern_pos, text_pos):
        """Recursively try to match pattern from pattern_pos against text from text_pos."""
        if pattern_pos == len(parsed_pattern) and text_pos == len(text):
            return True
        
        if pattern_pos >= len(parsed_pattern):
            return False
        
        element_type, quantifier = parsed_pattern[pattern_pos]
        
        def can_match(char_pos):
            """Check if the base element matches at text position char_pos."""
            if element_type == 'literal':
                return char_pos < len(text) and text[char_pos] == quantifier['char']
            elif element_type == 'any':
                return char_pos < len(text)
            elif element_type == 'class':
                return char_pos < len(text) and text[char_pos] in quantifier['chars_set']
            return False
        
        if quantifier is None:
            # No quantifier - must match exactly once
            if can_match(text_pos):
                return match_recursive(pattern_pos + 1, text_pos + 1)
            return False
        
        elif quantifier == '*':
            # Zero or more - try all possible counts
            for count in range(len(text) - text_pos + 1):
                new_text_pos = text_pos
                matched_count = 0
                
                # Try to match 'count' times
                temp_pos = text_pos
                while matched_count < count:
                    if not can_match(temp_pos):
                        break
                    temp_pos += 1
                    matched_count += 1
                
                new_text_pos = text_pos + matched_count
                
                if match_recursive(pattern_pos + 1, new_text_pos):
                    return True
            return False
        
        elif quantifier == '+':
            # One or more - need at least one match first
            for count in range(1, len(text) - text_pos + 2):
                temp_pos = text_pos
                matched_count = 0
                
                while matched_count < count:
                    if not can_match(temp_pos):
                        break
                    temp_pos += 1
                    matched_count += 1
                
                new_text_pos = text_pos + matched_count
                
                if matched_count >= 1 and match_recursive(pattern_pos + 1, new_text_pos):
                    return True
            return False
        
        elif quantifier == '?':
            # Zero or one - try both possibilities
            # Try zero matches
            if match_recursive(pattern_pos + 1, text_pos):
                return True
            # Try one match
            if can_match(text_pos):
                if match_recursive(pattern_pos + 1, text_pos + 1):
                    return True
            return False
        
        return False
    
    # Parse the pattern into elements
    parsed_pattern = []
    i = 0
    
    while i < len(pattern):
        elem_type = None
        quant_dict = {}
        quantifier = None
        
        if pattern[i] == '[':
            # Character class
            chars_set, negated, end_pos = parse_chars_class(pattern, i + 1)
            elem_type = 'class'
            quant_dict['chars_set'] = chars_set
            i = end_pos
        elif pattern[i] == '.':
            elem_type = 'any'
            i += 1
        else:
            # Literal character
            if i >= len(pattern):
                break
            elem_type = 'literal'
            quant_dict['char'] = pattern[i]
            i += 1
        
        # Check for quantifier
        if i < len(pattern) and pattern[i] in '*+?':
            quantifier = pattern[i]
            i += 1
        
        parsed_pattern.append((elem_type, {'quantifier': quantifier, **quant_dict}))
    
    return match_recursive(0, 0)
