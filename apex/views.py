import base64
import hmac
import time

from wtforms import TextField
from wtforms import validators
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
from pyramid.util import DottedNameResolver

from pyramid_mailer.message import Message

from apex.lib.apex import apex_settings
from apex.lib.apex import apexid_from_token
from apex.lib.apex import apex_email_forgot
from apex.lib.apex import auth_provider
from apex.lib.apex import generate_velruse_forms
from apex.lib.apex import provider_forms
from apex.lib.flash import flash
from apex.models import AuthGroup
from apex.models import AuthUser
from apex.models import DBSession
from apex.forms import ChangePasswordForm
from apex.forms import ForgotForm
from apex.forms import ResetPasswordForm
from apex.forms import LoginForm


def login(request):
    title = _('Login')
    came_from = request.GET.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))

    if asbool(apex_settings('use_recaptcha_on_login')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            LoginForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )
    form = LoginForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})
    
    
    velruse_forms = generate_velruse_forms(request, came_from)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_username(form.data.get('username'))
        if user:
            headers = remember(request, user.id)
            return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'velruse_forms': velruse_forms, \
            'action': 'login'}

def logout(request):
    headers = forget(request)
    return HTTPFound(location=route_url(apex_settings('came_from_route'), \
                     request), headers=headers)

def change_password(request):
    title = _('Change your Password')
    
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))
    form = ChangePasswordForm(request.POST)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_id(authenticated_userid(request))
        user.password = form.data['password']
        DBSession.merge(user)
        DBSession.flush()
        return HTTPFound(location=came_from)

    return {'title': title, 'form': form, 'action': 'changepass'}
     
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
                return HTTPFound(location=route_url('apex_login', \
                                          request))
        if form.data['username']:
            user = AuthUser.get_by_username(form.data['username'])
        if user:
            timestamp = time.time()+3600
            hmac_key = hmac.new('%s:%s:%d' % (str(user.id), \
                                apex_settings('auth_secret'), timestamp), \
                                user.email).hexdigest()[0:10]
            time_key = base64.urlsafe_b64encode('%d' % timestamp)
            email_hash = '%s%s' % (hmac_key, time_key)
            apex_email_forgot(request, user.id, user.email, email_hash)
            flash(_('Password Reset email sent.'))
            return HTTPFound(location=route_url('apex_login', \
                                                request))
        flash(_('An error occurred, please contact the support team.'))
    return {'title': title, 'form': form, 'action': 'forgot'}

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
        submitted_hmac = request.matchdict.get('hmac')
        current_time = time.time()
        time_key = int(base64.b64decode(submitted_hmac[10:]))
        if current_time < time_key:
            hmac_key = hmac.new('%s:%s:%d' % (str(user.id), \
                                apex_settings('auth_secret'), time_key), \
                                user.email).hexdigest()[0:10]
            if hmac_key == submitted_hmac[0:10]:
                user.password = form.data['password']
                DBSession.merge(user)
                DBSession.flush()
                flash(_('Password Changed. Please log in.'))
                return HTTPFound(location=route_url('apex_login', \
                                                    request))
            else:
                flash(_('Invalid request, please try again'))
                return HTTPFound(location=route_url('apex_forgot', \
                                                    request))
    return {'title': title, 'form': form, 'action': 'reset'}

def register(request):
    title = _('Register')
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))
    velruse_forms = generate_velruse_forms(request, came_from)

    #This fixes the issue with RegisterForm throwing an UnboundLocalError
    if apex_settings('register_form_class'):
        resolver = DottedNameResolver(apex_settings('register_form_class').split('.')[0])
        RegisterForm = resolver.resolve(apex_settings('register_form_class'))
    else:
        from apex.forms import RegisterForm

    if asbool(apex_settings('use_recaptcha_on_register')):
        if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
            RegisterForm.captcha = RecaptchaField(
                public_key=apex_settings('recaptcha_public_key'),
                private_key=apex_settings('recaptcha_private_key'),
            )

    form = RegisterForm(request.POST, captcha={'ip_address': request.environ['REMOTE_ADDR']})
    if request.method == 'POST' and form.validate():
        user = form.save()

        headers = remember(request, user.id)
        return HTTPFound(location=came_from, headers=headers)
        
    return {'title': title, 'form': form, 'velruse_forms': velruse_forms, \
            'action': 'register'}

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
                if apex_settings('default_user_group'):
                    group = DBSession.query(AuthGroup). \
                       filter(AuthGroup.name== \
                           apex_settings('default_user_group')).one()
                    user.groups.append(group)
                if apex_settings('create_openid_after'):
                    resolver = DottedNameResolver( \
                        apex_settings('create_openid_after').split('.')[0])
                    openid_after = resolver.resolve( \
                                       apex_settings('create_openid_after'))
                    openid_after().after_signup(user)
                DBSession.flush()
            if apex_settings('openid_required'):
                openid_required = False
                for required in apex_settings('openid_required').split(','):
                    if not getattr(user, required):
                        openid_required = True
                if openid_required:
                    request.session['id'] = user.id
                    return HTTPFound(location='%s?came_from=%s' % \
                        (route_url('apex_openid_required', request), \
                        request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))))
            headers = remember(request, user.id)
            redir = request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))
            flash(_('Successfully Logged in, welcome!'), 'success')
    return HTTPFound(location=redir, headers=headers)

def openid_required(request):
    title = _('OpenID Registration')
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))

    #This fixes the issue with RegisterForm throwing an UnboundLocalError
    if apex_settings('openid_register_form_class'):
        resolver = DottedNameResolver(apex_settings('openid_register_form_class').split('.')[0])
        OpenIDRequiredForm = resolver.resolve( \
                                 apex_settings('openid_register_form_class'))
    else:
        from apex.forms import OpenIDRequiredForm

    for required in apex_settings('openid_required').split(','):
        setattr(OpenIDRequiredForm, required, \
            TextField(required, [validators.Required()]))

    form = OpenIDRequiredForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_id(request.session['id'])
        for required in apex_settings('openid_required').split(','):
            setattr(user, required, form.data[required])
        DBSession.merge(user)
        DBSession.flush()
        headers = remember(request, user.id)
        return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'action': 'openid_required'}

def forbidden(request):
    flash(_('Not logged in, please log in'), 'error')
    return HTTPFound(location='%s?came_from=%s' %
                    (route_url('apex_login', request),
                    current_route_url(request)))
