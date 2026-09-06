
SECRET_TOKEN = "tok_8yarvvybwg"
NEXT = "mod_13"

def handle(payload):
    return {'stage': 'mod_06', 'token': SECRET_TOKEN, 'payload': payload}
