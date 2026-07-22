import re

def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: "aaabcc" returns "3a1b2c".
    """
    if not text:
        return ""

    encoded_parts = []
    i = 0
    n = len(text)

    while i < n:
        current_char = text[i]
        count = 1
        j = i + 1
        while j < n and text[j] == current_char:
            count += 1
            j += 1
        
        encoded_parts.append(f"{count}{current_char}")
        i = j  # Move index to the start of the next run

    return "".join(encoded_parts)

def decode(encoded: str) -> str:
    """
    Decodes an encoded string back to its original form.
    Handles multi-digit counts.
    Example: "3a12b" decodes to "aaabbbbbbbbbb".
    """
    if not encoded:
        return ""

    decoded_parts = []
    i = 0
    n = len(encoded)

    while i < n:
        # 1. Parse the count (which must be digits)
        count_str = ""
        start_of_digits = i
        while i < n and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if not count_str:
            # Should not happen for valid input, but handles malformed strings gracefully
            break

        try:
            count = int(count_str)
        except ValueError:
            # Safety break if conversion fails
            break

        # 2. The next character must be the repeated character
        if i >= n:
            # Malformed input (ends with count but no char)
            break
        
        char = encoded[i]
        i += 1 # Move past the character

        # 3. Append the reconstructed segment
        decoded_parts.append(char * count)

    return "".join(decoded_parts)

if __name__ == '__main__':
    # Test cases for encode
    print(f"Test 'aaabcc': {encode('aaabcc')}") # Expected: 3a1b2c
    print(f"Test 'abcde': {encode('abcde')}")   # Expected: 1a1b1c1d1e
    print(f"Test 'aaaaa': {encode('aaaaa')}")   # Expected: 5a
    print(f"Test '': {encode('')}")             # Expected: ""

    # Test cases for decode
    print(f"Test '3a1b2c' -> '{decode('3a1b2c')}'") # Expected: aaabbcc
    print(f"Test '5a' -> '{decode('5a')}'")       # Expected: aaaaa
    print(f"Test '1a1b1c1d1e' -> '{decode('1a1b1c1d1e')}'") # Expected: abcde
    print(f"Test '' -> '{decode('')}'")           # Expected: ""

    # Test multi-digit counts and inverse property
    s = "zzzyyyxaaaaabbbbccccccccccdde"
    encoded_s = encode(s)
    decoded_s = decode(encoded_s)
    print(f"\nOriginal String: {s}")
    print(f"Encoded: {encoded_s}")
    print(f"Decoded: {decoded_s}")
    assert s == decoded_s

    # Test case with large counts
    s_large = "A" * 12 + "B" * 3
    encoded_s_large = encode(s_large)
    decoded_s_large = decode(encoded_s_large)
    print(f"\nOriginal String: {s_large}")
    print(f"Encoded: {encoded_s_large}")
    print(f"Decoded: {decoded_s_large}")
    assert s_large == decoded_s_large
