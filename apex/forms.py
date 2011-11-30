from wtforms import Form
from wtforms import (
    HiddenField,
    PasswordField,
    TextField,
    validators,
)

from apex import MessageFactory as _
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.threadlocal import (
    get_current_registry,
    get_current_request,
)

from apex.models import DBSession, AuthGroup, AuthUser
from apex.lib.form import ExtendedForm
from apex.lib.settings import apex_settings

class RegisterForm(ExtendedForm):
    """ Registration Form
    """
    username = TextField(_('Username'), [validators.Required(), \
                         validators.Length(min=4, max=25)])
    password = PasswordField(_('Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat Password'), [validators.Required()])
    email = TextField(_('Email Address'), [validators.Required(), \
                      validators.Email()])

    def validate_email(form, field):
        need_verif = apex_settings('need_mail_verification')
        if need_verif and not field.data:
            raise validators.ValidationError(_('Sorry but you need to input an email.'))

    def validate_username(form, field):
        if AuthUser.get_by_username(field.data) is not None:
            raise validators.ValidationError(_('Sorry that username already exists.'))

    def create_user(self, username):
        user = AuthUser(
            username=username,
            password=self.data.get('password', ''),
            email=self.data['email'],
        )
        DBSession.add(user)
        settings = get_current_registry().settings
        if settings.has_key('apex.default_user_group'):
            group = DBSession.query(AuthGroup). \
               filter(AuthGroup.name==settings['apex.default_user_group']).one()
            user.groups.append(group)
        DBSession.flush()

        return user

    def save(self):
        new_user = self.create_user(self.data['username'])
        self.after_signup(new_user)
        return new_user

    def after_signup(self, user, **kwargs):
        """ Function to be overloaded and called after form submission
        to allow you the ability to save additional form data or perform
        extra actions after the form submission.
        """
        pass


class UseraddForm(RegisterForm):
    def __init__(self, *args, **kwargs):
        RegisterForm.__init__(self, *args, **kwargs)
        delattr(self, 'password2')
        delattr(self, 'password')

class ChangePasswordForm(ExtendedForm):
    """ Change Password Form
    """
    old_password = PasswordField(_('Old Password'), [validators.Required()])
    password = PasswordField(_('New Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat New Password'), [validators.Required()])

    def validate_old_password(form, field):
        request = get_current_request()
        if not AuthUser.check_password(id=authenticated_userid(request), \
                                       password=field.data):
            raise validators.ValidationError(_('Your old password doesn\'t match'))

class LoginForm(ExtendedForm):
    username = TextField(_('Username'), validators=[validators.Required()])
    password = PasswordField(_('Password'), validators=[validators.Required()])
    came_from = HiddenField('')

    def clean(self):
        errors = []
        if not AuthUser.check_password(username=self.data.get('username'), \
                                       password=self.data.get('password')):
            errors.append(_('Login Error -- please try again'))
        return errors

class ForgotForm(ExtendedForm):
    username = TextField(_('Username'))
    label = HiddenField(label='Or')
    email = TextField(_('Email Address'), [validators.Optional(), \
                                           validators.Email()])
    label = HiddenField(label='')
    label = HiddenField(label=_('If your username and email weren\'t found, ' \
                              'you may have logged in with a login ' \
                              'provider and didn\'t set your email ' \
                              'address.'))

    """ I realize the potential issue here, someone could continuously
        hit the page to find valid username/email combinations and leak
        information, however, that is an enhancement that will be added
        at a later point.
    """
    def validate_username(form, field):
        if AuthUser.get_by_username(field.data) is None:
            raise validators.ValidationError(_('Sorry that username doesn\'t exist.'))

    def validate_email(form, field):
        if AuthUser.get_by_email(field.data) is None:
            raise validators.ValidationError(_('Sorry that email doesn\'t exist.'))

    def clean(self):
        errors = []
        if not self.data.get('username') and not self.data.get('email'):
            errors.append(_('You need to specify either a Username or ' \
                            'Email address'))
        return errors

class ResetPasswordForm(ExtendedForm):
    password = PasswordField(_('New Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat New Password'), [validators.Required()])

class OAuthForm(ExtendedForm):
    end_point = HiddenField('')
    csrf_token = HiddenField('')

class OpenIdLogin(OAuthForm):
    provider_name = 'openid'
    provider_proper_name = 'OpenID'

    openid_identifier = TextField(_('OpenID Identifier'), \
                                  [validators.Required()])

class GoogleLogin(OAuthForm):
    provider_name = 'google'
    provider_proper_name = 'Google'

class FacebookLogin(OAuthForm):
    provider_name = 'facebook'
    provider_proper_name = 'Facebook'
    scope = HiddenField('')

class YahooLogin(OAuthForm):
    provider_name = 'yahoo'
    provider_proper_name = 'Yahoo'

class TwitterLogin(OAuthForm):
    provider_name = 'twitter'
    provider_proper_name = 'Twitter'

class WindowsLiveLogin(OAuthForm):
    provider_name = 'live'
    provider_proper_name = 'Microsoft Live'

class GithubLogin(OAuthForm):
    provider_name = 'github'
    provider_proper_name = 'Github'

class OpenIDRequiredForm(ExtendedForm):
    pass
