def encode(text: str) -> str:
    """Run-length encode the input string.
    Each run of identical characters becomes <count><char>.
    Single characters are encoded with a count of 1.
    """
    if not text:
        return ""
    result = []
    count = 1
    prev = text[0]
    for ch in text[1:]:
        if ch == prev:
            count += 1
        else:
            result.append(str(count))
            result.append(prev)
            prev = ch
            count = 1
    # append the final run
    result.append(str(count))
    result.append(prev)
    return "".join(result)


def decode(encoded: str) -> str:
    """Decode a run-length encoded string back to the original.
    Counts may be multi-digit (e.g., "12a" -> "aaaaaaaaaaaa").
    """
    if not encoded:
        return ""
    result = []
    i = 0
    n = len(encoded)
    while i < n:
        # accumulate digits for the count
        j = i
        while j < n and encoded[j].isdigit():
            j += 1
        # j now points to the character
        count = int(encoded[i:j])
        char = encoded[j]
        result.append(char * count)
        i = j + 1
    return "".join(result)
