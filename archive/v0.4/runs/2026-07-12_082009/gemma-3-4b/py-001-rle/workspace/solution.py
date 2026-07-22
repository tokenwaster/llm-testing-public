def encode(text: str) -> str:
    """Compresses runs of repeated characters into <count><char>.

    Example: encode("aaabcc") returns "3a1b2c". Single characters still get a count of 1.
    encode("") returns "". Input contains only letters (a-z, A-Z); encoding is case-sensitive.
    """
    if not text:
        return ""

    encoded_string = ""
    count = 1
    for i in range(len(text)):
        if i + 1 < len(text) and text[i] == text[i + 1]:
            count += 1
        else:
            encoded_string += str(count) + text[i]
            count = 1

    return encoded_string


def decode(encoded: str) -> str:
    """The exact inverse of encode. Counts may be multi-digit."""
    if not encoded:
        return ""

    decoded_string = ""
    i = 0
    while i < len(encoded):
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1

        if not count_str:
            break  # Handle potential errors if the input is malformed

        count = int(count_str)
        char = encoded[i]
        decoded_string += char * count
        i += 1

    return decoded_string
