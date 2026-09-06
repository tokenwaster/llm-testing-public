
SECRET_TOKEN = "tok_rpzxwsr74x"
NEXT = "mod_06"

def handle(payload):
    return {'stage': 'mod_19', 'token': SECRET_TOKEN, 'payload': payload}
