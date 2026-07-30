
SECRET_TOKEN = "tok_3qbp8jpsm5"
NEXT = "mod_07"

def handle(payload):
    return {'stage': 'mod_18', 'token': SECRET_TOKEN, 'payload': payload}
