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
        
        # Format: count followed by the character
        encoded_parts.append(f"{count}{current_char}")
        i = j  # Move index past the run

    return "".join(encoded_parts)


def decode(encoded: str) -> str:
    """
    Decodes an encoded string back to its original form. 
    Handles multi-digit counts (e.g., "12a" decodes to 'a' repeated 12 times).
    """
    if not encoded:
        return ""

    decoded_parts = []
    i = 0
    n = len(encoded)

    while i < n:
        # 1. Parse the count (which must be digits)
        count_str = ""
        start_index = i
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

        # Reconstruct the sequence
        decoded_parts.append(char * count)

    return "".join(decoded_parts)

if __name__ == '__main__':
    # Test cases for encode/decode cycle verification
    tests = [
        ("", "", "")), # Empty string
        ("abcde", "1a1b1c1d1e", "abcde"), # Single occurrences
        ("aaabbbcc", "3a2b2c", "aaabbbcc"), # Mixed runs
        ("aaaaa", "5a", "aaaaa"), # Long run
        ("AABBCCDD", "1A1A1B1C1D", "AABBCCDD") # Case sensitivity check (assuming input is always letters)
    ]

    print("--- Running Verification Tests ---")
    for original, expected_encoded, expected_decoded in tests:
        # Test 1: Encode -> Check against expected encoded format
        actual_encoded = encode(original)
        assert actual_encoded == expected_encoded, f"FAIL ENCODE: Input '{original}'. Expected '{expected_encoded}', Got '{actual_encoded}'."
        print(f"PASS ENCODE: '{original}' -> '{actual_encoded}'")

        # Test 2: Decode -> Check against expected decoded output
        actual_decoded = decode(actual_encoded)
        assert actual_decoded == expected_decoded, f"FAIL DECODE: Encoded '{actual_encoded}'. Expected '{expected_decoded}', Got '{actual_decoded}'."
        print(f"PASS DECODE: '{actual_encoded}' -> '{actual_decoded}'")

    # Test 3: Full cycle check (decode(encode(s)) == s)
    print("\n--- Running Cycle Check ---")
    cycle_tests = [
        ("hello world", "1h1e2l1o1w1o1r1l1d", "hello world"),
        ("aaabcc", "3a1b2c", "aaabcc"), # Prompt example check
        ("ZzZaA", "1Z1z1Z1a1A", "ZzZaA") # Mixed case/runs
    ]

    for original, _, _ in cycle_tests:
        encoded = encode(original)
        decoded = decode(encoded)
        assert decoded == original, f"FAIL CYCLE CHECK: Input '{original}'. Decoded result was '{decoded}'."
        print(f"PASS CYCLE CHECK: '{original}' -> ... -> '{decoded}'")

    print("\nAll tests passed successfully.")
