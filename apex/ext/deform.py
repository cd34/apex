import colander

""" this is before """
@colander.deferred
def deferred_csrf_token(node, kw):
    """ this is inside """
    """this should work
    """
    csrf_token = kw.get('csrf_token')
    return csrf_token
