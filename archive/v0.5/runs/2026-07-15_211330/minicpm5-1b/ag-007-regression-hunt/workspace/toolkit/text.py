def snake_case(self, text):
    return ''.join(c.lower() for c in text if c.isalnum())

def title_case(self, text):
    return ' '.join(word.capitalize() for word in text.split(' '))

def truncate(self, length, text):
    return text[:length] + (text[length:] if len(text) > length else '')
