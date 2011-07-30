import hmac

from velruse.app import parse_config_file
from wtfrecaptcha.fields import RecaptchaField

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import forget
from pyramid.security import remember
from pyramid.settings import asbool
from pyramid.url import current_route_url
from pyramid.url import route_url

from pyramid_mailer.message import Message

from pyramid_apex.lib.apex import apex_settings
from pyramid_apex.lib.apex import apexid_from_token
from pyramid_apex.lib.apex import apex_email_forgot
from pyramid_apex.lib.apex import auth_provider
from pyramid_apex.lib.apex import provider_forms
from pyramid_apex.lib.flash import flash
from pyramid_apex.models import AuthUser
from pyramid_apex.models import DBSession
from pyramid_apex.forms import ChangePasswordForm
from pyramid_apex.forms import ForgotForm
from pyramid_apex.forms import ResetPasswordForm
from pyramid_apex.forms import LoginForm
from pyramid_apex.forms import RegisterForm

def login(request):    
    if authenticated_userid(request):
        return HTTPFound(location=route_url(apex_settings('came_from_route'), request))

    title = _('Login')
    came_from = request.params.get('came_from', route_url(apex_settings('came_from_route'), request))

    if asbool(apex_settings('use_recaptcha_on_login')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            LoginForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )
    form = LoginForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})
    
    velruse_forms = []
    for provider in parse_config_file(apex_settings('velruse_config'))[0].keys():
        if provider_forms.has_key(provider):
            velruse_forms.append(provider_forms[provider](
                end_point='%s?csrf_token=%s&came_from=%s' % \
                 (request.route_url('pyramid_apex_callback'), \
                  request.session.get_csrf_token(),
                  came_from), \
                 csrf_token = request.session.get_csrf_token()
            ))            

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_username(form.data.get('username'))
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'velruse_forms': velruse_forms}

def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url(apex_settings('came_from_route'), \
                     request), headers=headers)

def change_password(request):
    if not authenticated_userid(request):
        return HTTPFound(location=route_url('pyramid_apex_login', request))

    title = _('Change your Password')
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
    title = _('Forgot My Password')
    if asbool(apex_settings('use_recaptcha_on_forgot')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            ForgotForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )
    form = ForgotForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})
    if request.method == 'POST' and form.validate():
        """ Special condition - if email imported from OpenID/Auth, we can
            direct the person to the appropriate login through a flash
            message.
        """
        if form.data['email']:
            user = AuthUser.get_by_email(form.data['email'])
            if user.login:
                provider_name = auth_provider.get(user.login[1], 'Unknown')
                flash(_('You used %s as your login provider' % \
                     provider_name))
                return HTTPFound(location=route_url('pyramid_apex_login', \
                                          request))
        if form.data['username']:
            user = AuthUser.get_by_username(form.data['username'])
        if user:
            hmac_key = hmac.new('%s:%s' % (str(user.id), \
                                apex_settings('auth_secret')), \
                                user.email).hexdigest()
            apex_email_forgot(request, user.id, user.email, hmac_key)
            flash(_('Password Reset email sent.'))
            return HTTPFound(location=route_url('pyramid_apex_login', \
                                                request))
        flash(_('An error occurred, please contact the support team.'))
    return {'title': title, 'form': form}

def reset_password(request):
    title = _('Reset My Password')
    if asbool(apex_settings('use_recaptcha_on_reset')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            ResetPasswordForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )
    form = ResetPasswordForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})
    if request.method == 'POST' and form.validate():
        user_id = request.matchdict.get('user_id')
        user = AuthUser.get_by_id(user_id)
        hmac_key = hmac.new('%s:%s' % (str(user.id), \
                            apex_settings('auth_secret')), \
                            user.email).hexdigest()
        if hmac_key == request.matchdict.get('hmac'):
            user.password = form.data['password']
            DBSession.merge(user)
            flash(_('Password Changed. Please log in.'))
            return HTTPFound(location=route_url('pyramid_apex_login', \
                                                request))
        else:
            flash(_('Invalid request, please try again'))
            return HTTPFound(location=route_url('pyramid_apex_forgot', \
                                                request))
    return {'title': title, 'form': form}
    
def register(request):
    title = _('Register')
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))

    if asbool(apex_settings('use_recaptcha_on_register')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            RegisterForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )

    form = RegisterForm(request.POST, captcha={'ip_address': request.environ['REMOTE_ADDR']})
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
    redir = request.GET.get('came_from', \
                route_url(apex_settings('came_from_route'), request))
    headers = []
    if 'token' in request.POST:
        auth = apexid_from_token(request.POST['token'])
        if auth:
            user = AuthUser.get_by_login(auth['apexid'])
            if not user:
                user = AuthUser(
                    login=auth['apexid'],
                )
                if auth['profile'].has_key('verifiedEmail'):
                    user.email = auth['profile']['verifiedEmail']
                DBSession.add(user)
                DBSession.flush()
            headers = remember(request, user.id)
            redir = request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))
            flash(_('Successfully Logged in, welcome!'), 'success')
    return HTTPFound(location=redir, headers=headers)

def forbidden(request):
    flash(_('Not logged in, please log in'), 'error')
    return HTTPFound(location='%s?came_from=%s' %
                    (route_url('pyramid_apex_login', request),
                    current_route_url(request)))
