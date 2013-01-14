import base64
import hmac
import time

from wtforms import TextField
from wtforms import validators
from wtforms.ext.sqlalchemy.orm import model_form

from wtfrecaptcha.fields import RecaptchaField

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.settings import asbool
from pyramid.url import current_route_url
from pyramid.url import route_url

from apex import MessageFactory as _
from apex.lib.db import merge_session_with_post
from apex.lib.libapex import (apex_email_forgot,
                              apexid_from_token,
                              apex_remember,
                              apex_settings,
                              generate_velruse_forms,
                              get_came_from,
                              get_module)
from apex.lib.flash import flash
from apex.lib.form import ExtendedForm
from apex.models import AuthGroup
from apex.models import AuthID
from apex.models import AuthUser
from apex.models import DBSession
from apex.forms import ChangePasswordForm
from apex.forms import ForgotForm
from apex.forms import ResetPasswordForm
from apex.forms import LoginForm


def login(request):
    """ login(request)
    No return value

    Function called from route_url('apex_login', request)
    """
    title = _('You need to login')
    came_from = get_came_from(request)
    if not apex_settings('exclude_local'):
        if asbool(apex_settings('use_recaptcha_on_login')):
            if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
                LoginForm.captcha = RecaptchaField(
                    public_key=apex_settings('recaptcha_public_key'),
                    private_key=apex_settings('recaptcha_private_key'),
                )
            form = LoginForm(request.POST,
                            captcha={'ip_address': request.environ['REMOTE_ADDR']})
        else:
            form = LoginForm(request.POST)
    else:
        form = None

    velruse_forms = generate_velruse_forms(request, came_from)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_login(form.data.get('login'))
        if user:
            headers = apex_remember(request, user, \
                max_age=apex_settings('max_cookie_age', None))
            return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'velruse_forms': velruse_forms, \
            'form_url': request.route_url('apex_login'),
            'action': 'login'}

def logout(request):
    """ logout(request):
    no return value, called with route_url('apex_logout', request)
    """
    headers = forget(request)
    came_from = get_came_from(request)
    return HTTPFound(location=came_from, headers=headers)

def change_password(request):
    """ change_password(request):
    no return value, called with route_url('apex_change_password', request)
    FIXME doesn't adjust auth_user based on local ID, how do we handle multiple
        IDs that are local? Do we tell person that they don't have local
        permissions?
    """
    title = _('Change your Password')

    came_from = get_came_from(request)
    user = DBSession.query(AuthUser). \
               filter(AuthUser.auth_id==authenticated_userid(request)). \
               filter(AuthUser.provider=='local').first()
    form = ChangePasswordForm(request.POST, user_id=user.id)

    if request.method == 'POST' and form.validate():
        #user = AuthID.get_by_id(authenticated_userid(request))
        user.password = form.data['password']
        DBSession.merge(user)
        DBSession.flush()
        return HTTPFound(location=came_from)

    return {'title': title, 'form': form, 'action': 'changepass'}

def forgot_password(request):
    """ forgot_password(request):
    no return value, called with route_url('apex_forgot_password', request)
    """
    title = _('Forgot my password')

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
            if user.provider != 'local':
                provider_name = user.provider
                flash(_('You used %s as your login provider' % \
                     provider_name))
                return HTTPFound(location=route_url('apex_login', \
                                          request))
        if form.data['login']:
            user = AuthUser.get_by_login(form.data['login'])
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
    """ reset_password(request):
    no return value, called with route_url('apex_reset_password', request)
    """
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
                #FIXME reset email, no such attribute email
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

def activate(request):
    """
    """
    user_id = request.matchdict.get('user_id')
    user = AuthID.get_by_id(user_id)
    submitted_hmac = request.matchdict.get('hmac')
    current_time = time.time()
    time_key = int(base64.b64decode(submitted_hmac[10:]))
    if current_time < time_key:
        hmac_key = hmac.new('%s:%s:%d' % (str(user.id), \
                            apex_settings('auth_secret'), time_key), \
                            user.email).hexdigest()[0:10]
        if hmac_key == submitted_hmac[0:10]:
            user.active = 'Y'
            DBSession.merge(user)
            DBSession.flush()
            flash(_('Account activated. Please log in.'))
            return HTTPFound(location=route_url('apex_login', \
                                                request))
    flash(_('Invalid request, please try again'))
    return HTTPFound(location=route_url(apex_settings('came_from_route'), \
                                        request))

def register(request):
    """ register(request):
    no return value, called with route_url('apex_register', request)
    """
    title = _('Register')
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))
    velruse_forms = generate_velruse_forms(request, came_from)

    #This fixes the issue with RegisterForm throwing an UnboundLocalError
    if apex_settings('register_form_class'):
        RegisterForm = get_module(apex_settings('register_form_class'))
    else:
        from apex.forms import RegisterForm

    if not apex_settings('exclude_local'):
        if asbool(apex_settings('use_recaptcha_on_register')):
            if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
                RegisterForm.captcha = RecaptchaField(
                    public_key=apex_settings('recaptcha_public_key'),
                    private_key=apex_settings('recaptcha_private_key'),
                )

        form = RegisterForm(request.POST, captcha={'ip_address': request.environ['REMOTE_ADDR']})
    else:
        form = None

    if request.method == 'POST' and form.validate():
        user = form.save()

        headers = apex_remember(request, user)
        return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'velruse_forms': velruse_forms, \
            'action': 'register'}

def apex_callback(request):
    """ apex_callback(request):
    no return value, called with route_url('apex_callback', request)

    This is the URL that Velruse returns an OpenID request to
    """
    redir = request.GET.get('came_from', \
                route_url(apex_settings('came_from_route'), request))
    headers = []
    if 'token' in request.POST:
        auth = apexid_from_token(request)
        if auth:
            user = AuthUser.get_by_login(auth['id'])
            if not user:
                auth_info = auth['profile']['accounts'][0]
                id = AuthID()
                DBSession.add(id)
                user = AuthUser(
                    login=auth_info['userid'],
                    provider=auth_info['domain'],
                )
                if auth['profile'].has_key('verifiedEmail'):
                    user.email = auth['profile']['verifiedEmail']
                id.users.append(user)
                if apex_settings('default_user_group'):
                    for name in apex_settings('default_user_group'). \
                                              split(','):
                        group = DBSession.query(AuthGroup). \
                           filter(AuthGroup.name==name.strip()).one()
                        id.groups.append(group)
                if apex_settings('create_openid_after'):
                    openid_after = get_module(apex_settings('create_openid_after'))
                    openid_after().after_signup(request=request, user=user)
                DBSession.flush()
            if apex_settings('openid_required'):
                openid_required = False
                for required in apex_settings('openid_required').split(','):
                    if not getattr(user, required):
                        openid_required = True
                if openid_required:
                    request.session['id'] = id.id
                    request.session['userid'] = user.id
                    return HTTPFound(location='%s?came_from=%s' % \
                        (route_url('apex_openid_required', request), \
                        request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))))
            headers = apex_remember(request, user)
            redir = request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))
            flash(_('Successfully Logged in, welcome!'), 'success')
    return HTTPFound(location=redir, headers=headers)

def openid_required(request):
    """ openid_required(request)
    no return value

    If apex_settings.openid_required is set, and the ax/sx from the OpenID
    auth doesn't return the required fields, this is called which builds
    a dynamic form to ask for the missing inforation.

    Called on Registration or Login with OpenID Authentication.
    """
    title = _('OpenID Registration')
    came_from = request.params.get('came_from', \
                    route_url(apex_settings('came_from_route'), request))

    #This fixes the issue with RegisterForm throwing an UnboundLocalError
    if apex_settings('openid_register_form_class'):
        OpenIDRequiredForm = get_module(apex_settings('openid_register_form_class'))
    else:
        from apex.forms import OpenIDRequiredForm

    for required in apex_settings('openid_required').split(','):
        setattr(OpenIDRequiredForm, required, \
            TextField(required, [validators.Required()]))

    form = OpenIDRequiredForm(request.POST, \
               captcha={'ip_address': request.environ['REMOTE_ADDR']})

    if request.method == 'POST' and form.validate():
        """
            need to have the AuthUser id that corresponds to the login
            method.
        """
        user = AuthUser.get_by_id(request.session['userid'])
        for required in apex_settings('openid_required').split(','):
            setattr(user, required, form.data[required])
        DBSession.merge(user)
        DBSession.flush()
        headers = apex_remember(request, user)
        return HTTPFound(location=came_from, headers=headers)

    return {'title': title, 'form': form, 'action': 'openid_required'}

def forbidden(request):
    """ forbidden(request)
    No return value

    Called when user hits a resource that requires a permission and the
    user doesn't have the required permission. Will prompt for login.

    request.environ['repoze.bfg.message'] contains our forbidden error in case
    of a csrf problem. Proper solution is probably an error page that
    can be customized.

    bfg.routes.route and repoze.bfg.message are scheduled to be deprecated,
    however, corresponding objects are not present in the request to be able
    to determine why the Forbidden exception was called.

    **THIS WILL BREAK EVENTUALLY**
    **THIS DID BREAK WITH Pyramid 1.2a3**
    """
    if request.matched_route:
        flash(_('Not logged in, please log in'), 'error')
        return HTTPFound(location='%s?came_from=%s' %
                        (route_url('apex_login', request),
                        current_route_url(request)))
    else:
        return Response('Unknown error message')

def edit(request):
    """ edit(request)
        no return value, called with route_url('apex_edit', request)

        This function will only work if you have set apex.auth_profile.

        This is a very simple edit function it works off your auth_profile
        class, all columns inside your auth_profile class will be rendered.
    """
    title = _('Edit')

    ProfileForm = model_form(
        model=get_module(apex_settings('auth_profile')),
        base_class=ExtendedForm,
        exclude=('id', 'user_id'),
    )

    record = AuthUser.get_profile(request)
    form = ProfileForm(obj=record)
    if request.method == 'POST' and form.validate():
        record = merge_session_with_post(record, request.POST.items())
        DBSession.merge(record)
        DBSession.flush()
        flash(_('Profile Updated'))
        return HTTPFound(location=request.url)

    return {'title': title, 'form': form, 'action': 'edit'}
