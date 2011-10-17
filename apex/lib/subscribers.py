from pyramid.httpexceptions import HTTPForbidden
from pyramid.i18n import TranslationString as _
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid

from apex.lib.flash import flash
from apex.lib.libapex import apex_settings
from apex.models import AuthUser

def user(request):
    """ user object exposed to templates
    """
    user = None
    if authenticated_userid(request):
        user = AuthUser.get_by_id(authenticated_userid(request))
    return user

def csrf_validation(event):
    """ CSRF token validation Subscriber

        As of Pyramid 1.2a3, passing messages through HTTPForbidden broke,
        and don't appear to be exposed to exception handlers.

        It appears that we cannot decorate a view and have it affect an event
        until after the event has fired, so, temporarily we're going to 
        have to use a value in the config to specify a list of paths that
        should not have CSRF validation.

        Ideally, we'll be able to do

        ::
            @no_csrf
            @view_config(route_name='test')
            def test(request):

        which would prevent CSRF tracking on that view. With the event hooks,
        our decorator is not read until AFTER the event, which makes this
        method fail at this point.

        Temporarily, we'll use a field in the development.ini:

        apex.no_csrf = routename1:routename2

    """
    if event.request.method == 'POST':
        token = event.request.POST.get('csrf_token') or event.request.GET.get('csrf_token')
        no_csrf = apex_settings('no_csrf', '').split(':')
        
        if (token is None or token != event.request.session.get_csrf_token()) \
            and event.request.matched_route.name not in no_csrf:
            raise HTTPForbidden(_('CSRF token is missing or invalid'))

def add_renderer_globals(event):
    """ add globals to templates

    csrf_token - bare token
    csrf_token_field - hidden input field with token inserted
    flash - flash messages
    """

    request = event.get('request')
    if request is None:
        request = get_current_request()

    csrf_token = request.session.get_csrf_token()

    globs = {
        'csrf_token': csrf_token,
        'csrf_token_field': '<input type="hidden" name="csrf_token" value="%s" />' % csrf_token,
        'flash': flash,
    }
    event.update(globs)

def add_user_context(event):
    """ add user context to request object
    """
    request = event.request
    context = request.context
    request.user = user(request)
