
SECRET_TOKEN = "tok_28b6sh4z2y"
NEXT = "mod_05"

def handle(payload):
    return {'stage': 'mod_16', 'token': SECRET_TOKEN, 'payload': payload}
