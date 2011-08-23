from pyramid.httpexceptions import HTTPForbidden
from pyramid.i18n import TranslationString as _
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid

from apex.lib.flash import flash
from apex.models import AuthUser

def user(request):
    """ user object exposed to templates
    """
    user = None
    if authenticated_userid(request):
        user = AuthUser.get_by_id(authenticated_userid(request))
    return user

def csrf_validation(event):
    """ CSRF token exposed to templates
    """
    if event.request.method == 'POST':
        token = event.request.POST.get('csrf_token') or event.request.GET.get('csrf_token')
        if token is None or token != event.request.session.get_csrf_token():
            raise HTTPForbidden(_('CSRF token is missing or invalid'))

def add_renderer_globals(event):
    """ add globals to forms

    csrf_token - bare token
    csrf_token_field - hidden input field with token inserted
    flash - flash messages
    user - user object
    """

    request = event.get('request')
    if request is None:
        request = get_current_request()

    csrf_token = request.session.get_csrf_token()

    globs = {
        'csrf_token': csrf_token,
        'csrf_token_field': '<input type="hidden" name="csrf_token" value="%s" />' % csrf_token,
        'flash': flash,
        'user': user(request),
    }
    event.update(globs)

def add_user_context(event):
    """ add user context to request object
    """
    request = event.request
    context = request.context
    request.user = user(request)
