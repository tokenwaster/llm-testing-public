
SECRET_TOKEN = "tok_ezcm8gkrbg"
NEXT = "mod_15"

def handle(payload):
    return {'stage': 'mod_12', 'token': SECRET_TOKEN, 'payload': payload}
