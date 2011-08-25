def get_or_create(session, model, **kw):
    """ Django's get_or_create function

http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    """
    obj = session.query(model).filter_by(**kw).first()
    if obj:
        return obj
    else:
        obj = model(**kw)
        session.add(obj)
        session.flush()
        return obj
        
def merge_session_with_post(session, post):
    """ Basic function to merge data into an sql object.
        This function doesn't work with relations.
    """
    for key, value in post:
        setattr(session, key, value)
    return session
