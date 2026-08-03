
SECRET_TOKEN = "tok_2qxr894gm8"
NEXT = "mod_01"

def handle(payload):
    return {'stage': 'mod_11', 'token': SECRET_TOKEN, 'payload': payload}
