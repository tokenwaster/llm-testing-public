
SECRET_TOKEN = "tok_etmuezhuke"
NEXT = "mod_23"

def handle(payload):
    return {'stage': 'mod_10', 'token': SECRET_TOKEN, 'payload': payload}
