from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import authenticated_userid
from pyramid.url import route_url

from pyramid_apex.lib.apex import apex_settings
from pyramid_apex.lib.flash import flash

def login_required(wrapped):
    def wrapper(request):
        result = wrapped(request)
        if not authenticated_userid(request):
            flash(_('Not logged in, please log in'), 'error')
            return HTTPFound(location=route_url('pyramid_apex_login', request))
    return wrapper 