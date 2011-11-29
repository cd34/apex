import base64
import hmac
import time

from urllib import urlencode

from wtforms import TextField
from wtforms import validators
from wtforms.ext.sqlalchemy.orm import model_form

from wtfrecaptcha.fields import RecaptchaField

from pyramid.httpexceptions import HTTPFound
from apex import MessageFactory as _
from pyramid.response import Response
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import forget
from pyramid.settings import asbool
from pyramid.url import current_route_url
from pyramid.url import route_url

from pyramid_mailer.message import Message

from apex.lib.db import merge_session_with_post
from apex.lib.settings import apex_settings
from apex.lib.libapex import (
    get_velruse_token,
    get_providers,
    apexid_from_token,
    apex_email_forgot,
    apex_email_activate,
    apex_remember,
    auth_provider,
    generate_velruse_forms,
    get_module,
    provider_forms,
    apex_email,
)
from apex.lib.flash import flash
from apex.lib.form import ExtendedForm
from apex.models import AuthGroup
from apex.models import AuthUser
from apex.models import DBSession
from apex.forms import ChangePasswordForm
from apex.forms import ForgotForm
from apex.forms import ResetPasswordForm
from apex.forms import LoginForm


def get_came_from(request):
    return request.GET.get('came_from',
                           request.POST.get(
                               'came_from',
                               route_url(apex_settings('came_from_route'), request))
                          )


AUTOSUBMITED_VELRUSE_LDAP_FORM = """\
<html>
    <head>
        <title>LDAP transaction in progress</title>
    </head>
    <body onload="document.forms[0].submit();">
        <form action="%s" method="post" accept-charset="UTF-8"
         enctype="application/x-www-form-urlencoded">
        <input type="hidden" name="end_point" value="%s" />
        <input type="hidden" name="ldap_username" value="%s" />
        <input type="hidden" name="ldap_password" value="%s" />
        <input type="submit" value="Continue"/></form>
        <script>
            var elements = document.forms[0].elements;
            for (var i = 0; i < elements.length; i++) {
                elements[i].style.display = "none";
            }
        </script>
    </body>
</html>
"""


def search_user(username):
    user = AuthUser.get_by_username(username)
    if not user and '@' in user:
        user = AuthUser.get_by_email(username)
    else:
        user = AuthUser.get_by_login(username)
    return user

def login(request):
    """ login(request)
    No return value

    Function called from route_url('apex_login', request)
    """
    title = _('You need to login')
    came_from = get_came_from(request)
    velruse_forms = generate_velruse_forms(request, came_from)
    providers = get_providers()
    if 'local' not in apex_settings('provider_exclude', []):
        if asbool(apex_settings('use_recaptcha_on_login')):
            if apex_settings('recaptcha_public_key') and apex_settings('recaptcha_private_key'):
                LoginForm.captcha = RecaptchaField(
                    public_key=apex_settings('recaptcha_public_key'),
                    private_key=apex_settings('recaptcha_private_key'),
                )
        form = LoginForm(request.POST,
                         captcha={'ip_address': request.environ['REMOTE_ADDR']})
    else:
        form = None

    for vform in velruse_forms:
        if getattr(vform, 'velruse_login', None):
            vform.action = vform.velruse_login

    # allow to include this as a portlet inside other pages
    if (request.method == 'POST'
        and (request.route_url('apex_login') in request.url)):
        local_status = form.validate()
        username = form.data.get('username')
        password = form.data.get('password')
        user = search_user(username)
        if local_status and user:
            if user.active == 'Y':
                headers = apex_remember(request, user.id)
                return HTTPFound(location=came_from, headers=headers)
        else:
            end_point='%s?%s' % (
                request.route_url('apex_callback'),
                urlencode(dict(
                    csrf_token=request.session.get_csrf_token(),
                    came_from=came_from,
                ))
            )
            # try ldap auth if present on velruse
            # idea is to let the browser to the request with
            # an autosubmitted form
            if 'velruse.providers.ldapprovider' in providers:
                response = AUTOSUBMITED_VELRUSE_LDAP_FORM%(
                    providers['velruse.providers.ldapprovider']['login'],
                    end_point,
                    username,
                    password)
                return Response(response)

    return {'title': title,
            'form': form,
            'velruse_forms': velruse_forms,
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
    """
    title = _('Change your Password')

    came_from = get_came_from(request)
    form = ChangePasswordForm(request.POST)

    if request.method == 'POST' and form.validate():
        user = AuthUser.get_by_id(authenticated_userid(request))
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
    user = AuthUser.get_by_id(user_id)
    submitted_hmac = request.matchdict.get('hmac')
    current_time = time.time()
    time_key = int(base64.b64decode(submitted_hmac[10:]))
    if current_time < time_key:
        hmac_key = hmac.new('%s:%s:%d' % (str(user.id),
                            apex_settings('auth_secret'), time_key),
                            user.email).hexdigest()[0:10]
        if hmac_key == submitted_hmac[0:10]:
            user.active = 'Y'
            DBSession.merge(user)
            DBSession.flush()
            flash(_('Account activated. Please log in.'))
            return HTTPFound(location=route_url('apex_login',
                                                request))
    flash(_('Invalid request, please try again'))
    return HTTPFound(location=route_url(apex_settings('came_from_route'),
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

    if 'local' not in apex_settings('provider_exclude', []):
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
        need_verif = apex_settings('need_mail_verification')
        response = HTTPFound(location=came_from)
        if need_verif:
            def begin_activation_email_process(user):
                timestamp = time.time()+3600
                hmac_key = hmac.new('%s:%s:%d' % (
                    str(user.id),
                    apex_settings('auth_secret'),
                    timestamp),
                    user.email).hexdigest()[0:10]
                time_key = base64.urlsafe_b64encode('%d' % timestamp)
                email_hash = '%s%s' % (hmac_key, time_key)
                apex_email_activate(request, user.id, user.email, email_hash)
            begin_activation_email_process(user)
            DBSession.add(user)
            user.active = 'N'
            DBSession.flush()
            flash(_('User sucessfully created, '
                    'please verify your account by clicking '
                    'on the link in the mail you just received from us !'), 'success')

            response = HTTPFound(location=came_from)
        else:
            headers = apex_remember(request, user.id)
            response = HTTPFound(location=came_from, headers=headers)
        return response

    return {'title': title,
            'form': form,
            'velruse_forms': velruse_forms,
            'action': 'register'}

def apex_callback(request):
    """ apex_callback(request):
    no return value, called with route_url('apex_callback', request)

    This is the URL that Velruse returns an OpenID request to
    """
    redir = request.GET.get('came_from',
                route_url(apex_settings('came_from_route'), request))
    headers = []
    login_failed = True
    reason = _('Login failed!')
    if 'token' in request.POST:
        token = request.POST['token']
        auth = apexid_from_token(token)
        if auth:
            login_failed = False
            user, email = None, ''
            if 'emails' in  auth['profile']:
                emails = auth['profile']['emails']
                if isinstance(emails[0], dict):
                    email = auth['profile']['emails'][0]['value']
                else:
                    email = auth['profile']['emails'][0]
            else:
                email = auth['profile'].get('verifiedEmail', '').strip()
            # first try by email
            if email:
                user = AuthUser.get_by_email(email)
            # then by id
            if user is None:
                user = search_user(auth['apexid'])
            if not user:
                user = AuthUser(
                    login=auth['apexid'],
                    username=auth['name'],
                )
                if email:
                    user.email = email
                DBSession.add(user)
                if apex_settings('default_user_group'):
                    for name in apex_settings('default_user_group'). \
                                              split(','):
                        group = DBSession.query(AuthGroup). \
                           filter(AuthGroup.name==name.strip()).one()
                        user.groups.append(group)
                if apex_settings('create_openid_after'):
                    openid_after = get_module(apex_settings('create_openid_after'))
                    request = openid_after().after_signup(request, user)
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
            headers = apex_remember(request, user.id)
            redir = request.GET.get('came_from', \
                        route_url(apex_settings('came_from_route'), request))
            flash(_('Successfully Logged in, welcome!'), 'success')
        else:
            auth = get_velruse_token(token)
            reasont = ''
            if auth.get('code', None):
                reasont += 'Code %s : ' % auth['code']
            if auth.get('description', ''):
                reasont += _(auth['description'])
            if reasont:
                reason = reasont
            login_failed = True
    if login_failed:
        flash(reason)
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
        user = AuthUser.get_by_id(request.session['id'])
        for required in apex_settings('openid_required').split(','):
            setattr(user, required, form.data[required])
        DBSession.merge(user)
        DBSession.flush()
        headers = apex_remember(request, user.id)
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
    if request.environ.has_key('bfg.routes.route'):
        flash(_('Not logged in, please log in'), 'error')
        return HTTPFound(location='%s?came_from=%s' %
                        (route_url('apex_login', request),
                        current_route_url(request)))
    else:
        return Response(request.environ.get('repoze.bfg.message', \
                        'Unknown error message'))

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
