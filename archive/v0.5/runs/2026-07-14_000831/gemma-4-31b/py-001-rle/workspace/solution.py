def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: "aaabcc" -> "3a1b2c"
    """
    if not text:
        return ""

    result = []
    count = 1
    
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            result.append(f"{count}{text[i - 1]}")
            count = 1
            
    # Append the final run
    result.append(f"{count}{text[-1]}")
    
    return "".join(result)


def decode(encoded: str) -> str:
    """
    The inverse of encode. Decodes <count><char> back into repeated characters.
    Example: "3a1b2c" -> "aaabcc"
    """
    if not encoded:
        return ""

    result = []
    digit_buffer = ""
    
    for char in encoded:
        if char.isdigit():
            digit_buffer += char
        else:
            # Convert accumulated digits to integer and multiply the character
            count = int(digit_buffer)
            result.append(char * count)
            digit_buffer = ""
            
    return "".join(result)
