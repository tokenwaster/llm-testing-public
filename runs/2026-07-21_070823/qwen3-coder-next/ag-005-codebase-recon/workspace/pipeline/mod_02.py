"""Handler for shard rebalancing."""

SECRET_TOKEN = "tok_qnuwgr2vn6"
NEXT = "mod_28"

def handle(payload):
    """Process one payload unit and forward."""
    return {'stage': 'mod_02', 'token': SECRET_TOKEN, 'payload': payload}
