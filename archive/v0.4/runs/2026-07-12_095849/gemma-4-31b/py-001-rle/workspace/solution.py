def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: "aaabcc" -> "3a1b2c"
    """
    if not text:
        return ""

    encoded_parts = []
    count = 1
    
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            encoded_parts.append(f"{count}{text[i - 1]}")
            count = 1
            
    # Append the final run
    encoded_parts.append(f"{count}{text[-1]}")
    
    return "".join(encoded_parts)


def decode(encoded: str) -> str:
    """
    The inverse of encode. Decodes <count><char> back into repeated characters.
    Counts may be multi-digit (e.g., "12a" -> 12 copies of 'a').
    """
    if not encoded:
        return ""

    decoded_parts = []
    digit_buffer = ""
    
    for char in encoded:
        if char.isdigit():
            digit_buffer += char
        else:
            # Convert accumulated digits to integer and multiply by the character
            count = int(digit_buffer)
            decoded_parts.append(char * count)
            digit_buffer = ""
            
    return "".join(decoded_parts)
