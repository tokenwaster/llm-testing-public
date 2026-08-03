def parse(text: str) -> object | None:
    """Parses a JSON document and returns the equivalent Python object."""

    i = 0
    def next_token():
        nonlocal i
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            return None
        char = text[i]
        if char in '\"\'[:][-:,/\\{}]+':
            i += 1
            res = ''
            while i < len(text) and text[i] != char:
                res += text[i]
                i += 1
            return res
        elif char.isdigit() or char == '-':
            res = ''
            while i < len(text) and (text[i].isdigit() or text[i] == '.' or text[i] == '-' ):
                res += text[i]
                i += 1
            try:
                return int(res) if res else None
            except ValueError:
                return float(res)
        elif char == '[' or char == ']':
            i += 1
            res = ''
            while i < len(text) and text[i] != char:
                res += text[i]
                i += 1
            return res
        elif char == '{' or char == '}':
            i += 1
            res = ''
            while i < len(text) and text[i] != char:
                res += text[i]
                i += 1
            return res
        elif char == 't' or char == 'f' or char == 'n':
            i += 1
            if text.startswith("true", i):
                return True
            elif text.startswith("false", i):
                return False
            elif text.startswith("null", i):
                return None
            else:
                return None
        elif char == 'u':
            i += 2
            try:
                return chr(int(text[i:i+4], 16))
            except ValueError:
                return None
        else:
            return None

    if not text:
        return None

    result = {}
    while True:
        key = next_token()
        if key is None:
            break
        if key == 'None':
            result[key] = None
            continue
        if key.startswith('"') and key.endswith('"'):
            result[key] = next_token()
        elif key.isdigit() or key.startswith('-'):
             result[key] = next_token()
        elif key == '[':
            arr = []
            while True:
                item = next_token()
                if item is None:
                    break
                if item == ']':
                    break
                if item == ',':
                  continue

                arr.append(parse(item))
            result[key] = arr
        elif key == '{':
            obj = {}
            while True:
                name = next_token()
                if name is None:
                    break
                if name == '}':
                    break
                if name.startswith('"') and name.endswith('"'):
                    value = next_token()
                    if value is None:
                        break
                    obj[name] = parse(value)

                elif name.isdigit() or name.startswith('-'):
                   obj[name] = parse(name)


                elif name == '[':
                  arr = []
                  while True:
                      item = next_token()
                      if item is None:
                          break
                      if item == ']':
                          break
                      if item == ',':
                        continue

                      arr.append(parse(item))
                  obj[name] = arr

                elif name == '{':
                    obj[name] = parse(name)
                elif name == 'true' or name == 'false' or name == 'null':
                   obj[name] = next_token()

                else:
                    obj[name] = None

            result[key] = obj
        else:
            break

    if i < len(text):
        return None

    if result:
      last_key = list(result.keys())[-1]
      if last_key == '}' or last_key == ']':
          return result
      else:
          return next_token()
    else:
        return next_token()
