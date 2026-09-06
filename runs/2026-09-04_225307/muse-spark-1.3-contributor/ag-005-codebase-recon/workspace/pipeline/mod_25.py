
SECRET_TOKEN = "tok_quqhqqyhwg"
NEXT = "mod_02"

def handle(payload):
    return {'stage': 'mod_25', 'token': SECRET_TOKEN, 'payload': payload}
