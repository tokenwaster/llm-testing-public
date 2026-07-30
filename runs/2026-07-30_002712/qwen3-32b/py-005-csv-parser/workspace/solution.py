def parse_csv(text: str) -> list[list[str]]:
    if not text:
        return []

    # Normalize line endings to '\n'
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = normalized.split('\n')

    # Remove trailing empty string from split
    if lines and lines[-1] == '':
        lines.pop()

    result = []
    
    for line in lines:
        fields = []
        current_field = []
        in_quotes = False

        i = 0
        while i < len(line):
            c = line[i]

            if not in_quotes:
                if c == ',':
                    # End of unquoted field
                    fields.append(''.join(current_field))
                    current_field = []
                    i += 1
                elif c == '"':
                    # Start of quoted field
                    in_quotes = True
                    i += 1
                else:
                    current_field.append(c)
                    i += 1
            else:  # Inside quotes
                if c == '"':
                    if i + 1 < len(line) and line[i+1] == '"':
                        # Escaped quote
                        current_field.append('"')
                        i += 2
                    else:
                        # End of quoted field
                        in_quotes = False
                        fields.append(''.join(current_field))
                        current_field = []
                        i += 1

                        if i < len(line):
                            if line[i] == ',':
                                i += 1
                            else:
                                raise ValueError("Malformed CSV: invalid character after closing quote")
                else:
                    current_field.append(c)
                    i += 1

        # Append any remaining field at end of line
        if not in_quotes and current_field:
            fields.append(''.join(current_field))
        elif in_quotes:
            raise ValueError("Unclosed quoted field")

        result.append(fields)

    return result
