from pyramid.httpexceptions import HTTPFound
from pyramid.security import Allow, Everyone, Authenticated, forget, remember, authenticated_userid
from pyramid.url import route_url

from pyramid_apex.lib import apex_settings
from pyramid_apex.models import DBSession, AuthUser
from pyramid_apex.forms import RegisterForm, LoginForm, ChangePasswordForm

#import bcrypt

def login(request):
    #print bcrypt.hashpw('testing', bcrypt.gensalt())
    
    if authenticated_userid(request):
        return HTTPFound(location=route_url('index', request))

    title = 'Login'
    came_from = request.params.get('came_from', route_url('index', request))
    form = LoginForm(request.POST)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_username(form.data.get('username'))
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form}

def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url('index', request), headers=headers)

def change_password(request):
    if not authenticated_userid(request):
        return HTTPFound(location=route_url('pyramid_auth_login', request))

    title = 'Change your Password'
    came_from = request.params.get('came_from', route_url('index', request))
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
    came_from = request.params.get('came_from', route_url('index', request))
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