def parse_csv(text: str) -> list[list[str]]:
    def split_records(text):
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        return text.split('\n')

    def parse_line(line):
        fields = []
        current_field = []
        in_quotes = False
        i = 0

        while i < len(line):
            char = line[i]
            if not in_quotes:
                if char == ',':
                    fields.append(''.join(current_field))
                    current_field = []
                    i += 1
                elif char == '"':
                    in_quotes = True
                    i += 1
                else:
                    if char == '\n':
                        raise ValueError("Newline outside quoted field")
                    current_field.append(char)
                    i += 1
            else:
                if char == '"':
                    if i + 1 < len(line) and line[i+1] == '"':
                        current_field.append('"')
                        i += 2
                    else:
                        in_quotes = False
                        i += 1
                        if i < len(line):
                            if line[i] != ',':
                                raise ValueError("Invalid character after closing quote")
                else:
                    current_field.append(char)
                    i += 1

        if in_quotes:
            raise ValueError("Unclosed quote in line")

        fields.append(''.join(current_field))
        return fields

    lines = split_records(text)
    result = []
    for line in lines:
        try:
            parsed_line = parse_line(line)
            result.append(parsed_line)
        except ValueError as e:
            if "Newline outside quoted field" in str(e):
                raise ValueError("Invalid CSV format: newline found outside of quotes")
            else:
                raise
    return result
