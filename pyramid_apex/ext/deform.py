import colander

@colander.deferred
def deferred_csrf_token(node, kw):
    csrf_token = kw.get('csrf_token')
    return csrf_token
