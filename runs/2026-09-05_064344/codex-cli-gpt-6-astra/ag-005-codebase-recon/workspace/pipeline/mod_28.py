
SECRET_TOKEN = "tok_3c4926768b"
NEXT = "mod_05"

def handle(payload):
    return {'stage': 'mod_28', 'token': SECRET_TOKEN, 'payload': payload}
