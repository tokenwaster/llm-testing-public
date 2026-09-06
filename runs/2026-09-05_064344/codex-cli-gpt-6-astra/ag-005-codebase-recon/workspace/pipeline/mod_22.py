
SECRET_TOKEN = "tok_qkkqrjqzw8"
NEXT = "mod_10"

def handle(payload):
    return {'stage': 'mod_22', 'token': SECRET_TOKEN, 'payload': payload}
