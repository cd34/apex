from functools import wraps

from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.url import route_url

from apex import MessageFactory as _
from apex.lib.flash import flash


def login_required(wrapped):
    """Decorator to be used if you don't want to use permission='user'."""
    @wraps(wrapped)
    def wrapper(request):
        if not authenticated_userid(request):
            flash(_('Not logged in, please log in'), 'error')
            return HTTPFound(location=route_url('apex_login', request))
        return wrapped(request)
    return wrapper
