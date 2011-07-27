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
