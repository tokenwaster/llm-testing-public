
SECRET_TOKEN = "tok_my3xuvyd3r"
NEXT = "mod_13"

def handle(payload):
    return {'stage': 'mod_01', 'token': SECRET_TOKEN, 'payload': payload}
