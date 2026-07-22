import re

def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: encode("aaabcc") -> "3a1b2c"
    """
    if not text:
        return ""
    
    encoded_parts = []
    current_char = text[0]
    current_count = 1
    
    for char in text[1:]:
        if char == current_char:
            current_count += 1
        else:
            encoded_parts.append(f"{current_count}{current_char}")
            current_char = char
            current_count = 1
            
    encoded_parts.append(f"{current_count}{current_char}")
    return "".join(encoded_parts)

def decode(encoded: str) -> str:
    """
    Decodes a run-length encoded string back to its original form.
    Example: decode("3a1b2c") -> "aaabcc"
    """
    if not encoded:
        return ""
    
    # Find all occurrences of <digits><character>
    pairs = re.findall(r'(\d+)([a-zA-Z])', encoded)
    decoded_parts = [char * int(count) for count, char in pairs]
    return "".join(decoded_parts)
