
SECRET_TOKEN = "tok_r8vhbf6ap9"
NEXT = "mod_11"

def handle(payload):
    return {'stage': 'mod_07', 'token': SECRET_TOKEN, 'payload': payload}
