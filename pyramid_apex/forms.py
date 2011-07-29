from wtforms import Form
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import TextField
from wtforms import validators

from pyramid.i18n import TranslationString as _
from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.threadlocal import get_current_request

from pyramid_apex.models import AuthUser
from pyramid_apex.lib.form import ExtendedForm

class RegisterForm(ExtendedForm):
    username = TextField(_('Username'), [validators.Required(), \
                         validators.Length(min=4, max=25)])
    password = PasswordField(_('Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat Password'), [validators.Required()])
    email = TextField(_('Email Address'), [validators.Required(), \
                      validators.Email()])

    def validate_username(form, field):
        if AuthUser.get_by_username(field.data) is not None:
            raise validators.ValidationError(_('Sorry that username already exists.'))

class ChangePasswordForm(ExtendedForm):
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
    label = HiddenField(label=_('If your username and email weren\'t found,<br>' \
                              'you may have logged in with a login<br>' \
                              'provider and didn\'t set your email<br>' \
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

class OAuthForm(ExtendedForm):
    end_point = HiddenField('')
    csrf_token = HiddenField('')

class OpenIdLogin(OAuthForm):
    provider_name = 'openid'

    openid_identifier = TextField(_('OpenID Identifier'), \
                                  [validators.Required()])

class GoogleLogin(OAuthForm):
    provider_name = 'google'

class FacebookLogin(OAuthForm):
    provider_name = 'facebook'
    
class YahooLogin(OAuthForm):
    provider_name = 'yahoo'
    
class TwitterLogin(OAuthForm):
    provider_name = 'twitter'
    
class WindowsLiveLogin(OAuthForm):
    provider_name = 'live'
