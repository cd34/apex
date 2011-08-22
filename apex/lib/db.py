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
