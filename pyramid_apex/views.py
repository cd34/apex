from pyramid.httpexceptions import HTTPFound
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import forget
from pyramid.security import remember
from pyramid.url import current_route_url
from pyramid.url import route_url

from pyramid_apex.lib import apex_settings
from pyramid_apex.lib.apex import apexid_from_token
from pyramid_apex.models import DBSession, AuthUser
from pyramid_apex.forms import RegisterForm
from pyramid_apex.forms import LoginForm
from pyramid_apex.forms import ChangePasswordForm

def login(request):
    if authenticated_userid(request):
        return HTTPFound(location=route_url(apex_settings('came_from_route'), request))

    title = 'Login'
    came_from = request.params.get('came_from', route_url(apex_settings('came_from_route'), request))
    form = LoginForm(request.POST)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_username(form.data.get('username'))
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form}

def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url(apex_settings('came_from_route'), \
                     request), headers=headers)

def change_password(request):
    if not authenticated_userid(request):
        return HTTPFound(location=route_url('pyramid_apex_login', request))

    title = 'Change your Password'
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))
    form = ChangePasswordForm(request.POST)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_id(authenticated_userid(request))
        user.password = form.data['password']
        DBSession.merge(user)
        return HTTPFound(location=came_from)

    return {'title': title, 'form': form}
            
def forgot_password(request):
    title = 'Forgot My Password'
    return {}
    
def register(request):
    title = 'Register'
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))
    form = RegisterForm(request.POST)
    if request.method == 'POST' and form.validate():
        user = AuthUser(
            username=form.data['username'],
            password=form.data['password'],
            email=form.data['email'],
        )
        DBSession.add(user)
        DBSession.flush()
        
        headers = remember(request, user.id)
        return HTTPFound(location=came_from, headers=headers)
        
    return {'title': title, 'form': form}

def apex_callback(request):
    auth = apexid_from_token(request.POST['token'])
    user = AuthUser.get_by_login(auth['apexid'])
    if not user:
        user = AuthUser(
            login=auth['apexid'],
        )
        DBSession.add(user)
        DBSession.flush()
    headers = remember(request, user.id)
    return HTTPFound(location='/', headers=headers)

def forbidden(request):
    return HTTPFound(location='%s?came_from=%s' %
                    (route_url('pyramid_apex_login', request),
                    current_route_url(request)))
