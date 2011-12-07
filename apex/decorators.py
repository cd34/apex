from pyramid.httpexceptions import HTTPFound
from apex import MessageFactory as _
from pyramid.security import authenticated_userid
from pyramid.url import route_url

from apex.lib.flash import flash

def login_required(wrapped):
    """ login_requred - Decorator to be used if you don't want to use
    permission='user'
    """
    def wrapper(request):
        result = wrapped(request)
        if not authenticated_userid(request):
            flash(_('Not logged in, please log in'), 'error')
            return HTTPFound(location=route_url('apex_login', request))
    return wrapper
