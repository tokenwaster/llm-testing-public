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
        
        # Format the count (as string) followed by the character
        encoded_parts.append(f"{count}{current_char}")
        i = j  # Move index i to the start of the next unique run

    return "".join(encoded_parts)

def decode(encoded: str) -> str:
    """
    Decodes an encoded string back to its original form.
    Handles multi-digit counts (e.g., "12a").
    """
    if not encoded:
        return ""

    decoded_parts = []
    i = 0
    n = len(encoded)

    while i < n:
        # 1. Parse the count (which consists of digits)
        count_str = ""
        start_of_digits = i
        
        # Read all consecutive digits
        while i < n and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if not count_str:
            # This should ideally not happen if the input is guaranteed to be valid,
            # but handles cases where we expect a count but find none.
            raise ValueError(f"Invalid encoded format at index {start_of_digits}: Expected count.")

        count = int(count_str)
        
        # 2. The next character must be the character being repeated
        if i >= n:
             raise ValueError("Invalid encoded format: Count found without trailing character.")
             
        char_to_repeat = encoded[i]
        i += 1 # Move past the character

        # Append the reconstructed segment
        decoded_parts.append(char_to_repeat * count)

    return "".join(decoded_parts)

if __name__ == '__main__':
    # Test cases for encode
    print(f"encode('aaabcc'): {encode('aaabcc')}") # Expected: 3a1b2c
    print(f"encode('abcde'): {encode('abcde')}")   # Expected: 1a1b1c1d1e
    print(f"encode('aaaaa'): {encode('aaaaa')}")   # Expected: 5a
    print(f"encode(''): {encode('')}")             # Expected: ""

    # Test cases for decode
    print(f"decode('3a1b2c'): {decode('3a1b2c')}") # Expected: aaabcc
    print(f"decode('5a'): {decode('5a')}")         # Expected: aaaaa
    print(f"decode('1a1b1c1d1e'): {decode('1a1b1c1d1e')}") # Expected: abcde
    print(f"decode(''): {decode('')}")             # Expected: ""

    # Test case for multi-digit counts and inverse property check
    s = "zzzyyyxaaaaabbbbccccccccccz"
    encoded_s = encode(s)
    decoded_s = decode(encoded_s)
    print(f"\nOriginal String (s): {s}")
    print(f"Encoded String: {encoded_s}")
    print(f"Decoded String: {decoded_s}")
    assert s == decoded_s, "Inverse property failed!"

    # Test case with large counts
    s_large = "a" * 12 + "b" * 3
    encoded_large = encode(s_large)
    decoded_large = decode(encoded_large)
    print(f"\nOriginal String (s_large): {s_large}")
    print(f"Encoded String: {encoded_large}")
    print(f"Decoded String: {decoded_large}")
    assert s_large == decoded_large, "Inverse property failed for large counts!"
