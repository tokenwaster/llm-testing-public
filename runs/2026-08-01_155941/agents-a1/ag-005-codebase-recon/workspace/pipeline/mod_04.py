
SECRET_TOKEN = "tok_gcq283jkcg"
NEXT = "mod_17"

def handle(payload):
    return {'stage': 'mod_04', 'token': SECRET_TOKEN, 'payload': payload}
