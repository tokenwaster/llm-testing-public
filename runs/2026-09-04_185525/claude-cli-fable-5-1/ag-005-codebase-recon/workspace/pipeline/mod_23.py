
SECRET_TOKEN = "tok_x9v9p3mptq"
NEXT = "mod_01"

def handle(payload):
    return {'stage': 'mod_23', 'token': SECRET_TOKEN, 'payload': payload}
