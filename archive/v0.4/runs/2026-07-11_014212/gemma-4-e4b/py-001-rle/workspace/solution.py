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
        
        # Count consecutive identical characters
        while j < n and text[j] == current_char:
            count += 1
            j += 1
        
        encoded_parts.append(f"{count}{current_char}")
        i = j  # Move index i to the start of the next run

    return "".join(encoded_parts)


def decode(encoded: str) -> str:
    """
    Decodes an encoded string back to its original form.
    Handles multi-digit counts (e.g., "12a" decodes to 12 copies of 'a').
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

        # 2. Parse the character (which must be the next non-digit character)
        if i >= n:
            # Malformed input: count found but no character follows
            break
            
        char = encoded[i]
        i += 1 # Move past the character

        # Append the repeated character
        decoded_parts.append(char * count)

    return "".join(decoded_parts)

if __name__ == '__main__':
    # Test cases for encode
    print(f"encode('aaabcc'): {encode('aaabcc')}") # Expected: 3a1b2c
    print(f"encode('abcde'): {encode('abcde')}")   # Expected: 1a1b1c1d1e
    print(f"encode('aaaaa'): {encode('aaaaa')}")   # Expected: 5a
    print(f"encode('AABBCC'): {encode('AABBCC')}") # Expected: 1A2B2C
    print(f"encode('') : '{encode('')}'")         # Expected: ''

    # Test cases for decode
    print(f"\ndecode('3a1b2c'): {decode('3a1b2c')}") # Expected: aaabc c
    print(f"decode('5a'): {decode('5a')}")         # Expected: aaaaa
    print(f"decode('1A2B2C'): {decode('1A2B2C')}") # Expected: ABCC
    print(f"decode('') : '{decode('')}'")         # Expected: ''

    # Test round trip property (Crucial check)
    test_strings = ["hello world", "aaaaa", "abcde", "", "ZzZZ"]
    for s in test_strings:
        encoded_s = encode(s)
        decoded_s = decode(encoded_s)
        assert decoded_s == s, f"Failed round trip for '{s}'. Encoded: {encoded_s}, Decoded: {decoded_s}"
    print("\nAll round-trip tests passed.")
