
SECRET_TOKEN = "tok_hqzzrkfb7p"
NEXT = "mod_21"

def handle(payload):
    return {'stage': 'mod_20', 'token': SECRET_TOKEN, 'payload': payload}
