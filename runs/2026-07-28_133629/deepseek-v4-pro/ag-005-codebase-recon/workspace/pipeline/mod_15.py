
SECRET_TOKEN = "tok_xnsuq2857q"
NEXT = "mod_08"

def handle(payload):
    return {'stage': 'mod_15', 'token': SECRET_TOKEN, 'payload': payload}
