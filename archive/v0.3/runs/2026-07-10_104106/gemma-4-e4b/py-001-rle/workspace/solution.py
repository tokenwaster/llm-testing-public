def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: "aaabcc" -> "3a1b2c".
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
        
        # Append count (as string) followed by the character
        encoded_parts.append(f"{count}{current_char}")
        i = j  # Move index i to the start of the next run

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
        start_index = i
        while i < n and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if not count_str:
            # This should theoretically not happen if the input is valid, 
            # but handles cases where a non-digit starts unexpectedly.
            raise ValueError(f"Invalid encoded format at index {start_index}: Expected digit count.")

        try:
            count = int(count_str)
        except ValueError:
             # Should be caught by the isdigit check, but good practice.
            raise ValueError("Failed to parse integer count.")


        # 2. The character must follow the digits
        if i >= n:
            raise ValueError("Invalid encoded format: Count found without trailing character.")

        char = encoded[i]
        i += 1 # Move past the character

        # Append the repeated character sequence
        decoded_parts.append(char * count)

    return "".join(decoded_parts)

if __name__ == '__main__':
    # Test cases for encode/decode cycle verification
    tests = [
        ("", "", "")), # Empty string
        ("abcde", "1a1b1c1d1e", "abcde"), # Single occurrences
        ("aaabbc", "3a2b1c", "aaabbc"), # Mixed runs
        ("aaaaa", "5a", "aaaaa"), # Single character run
        ("aabbccddeeffg", "2a2b2c2d2e2f1g", "aabbccddeeffg") # Multiple pairs
    ]

    print("--- Running Verification Tests ---")
    all_passed = True
    for input_str, expected_encoded, expected_decoded in tests:
        try:
            encoded_result = encode(input_str)
            if encoded_result != expected_encoded:
                print(f"FAIL (Encode): Input '{input_str}'. Expected '{expected_encoded}', Got '{encoded_result}'")
                all_passed = False
            else:
                decoded_result = decode(encoded_result)
                if decoded_result != input_str:
                    print(f"FAIL (Decode Cycle): Input '{input_str}'. Encoded '{encoded_result}', Decoded '{decoded_result}'")
                    all_passed = False
                else:
                    # print(f"PASS: {input_str} -> {encoded_result} -> {decoded_result}")
                    pass

        except Exception as e:
            print(f"FAIL (Exception): Input '{input_str}'. Error: {e}")
            all_passed = False

    if all_passed:
        print("\nAll basic tests passed successfully.")
