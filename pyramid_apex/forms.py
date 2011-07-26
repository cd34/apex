from wtforms import Form
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import TextField
from wtforms import validators

from pyramid.security import authenticated_userid
from pyramid.security import remember
from pyramid.threadlocal import get_current_request

from pyramid_apex.models import AuthUser
from pyramid_apex.lib.form import ExtendedForm

from wtforms.validators import ValidationError

class RegisterForm(ExtendedForm):
    username = TextField('Username', [validators.Required(), \
                         validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required(), \
                             validators.EqualTo('password2', \
                             message='Passwords must match')])
    password2 = PasswordField('Repeat Password', [validators.Required()])
    email = TextField('Email Address', [validators.Required(), \
                      validators.Email()])

    def validate_username(form, field):
        if AuthUser.get_by_username(field.data) is not None:
            raise ValidationError('Sorry that username already exists.')

class ChangePasswordForm(ExtendedForm):
    old_password = PasswordField('Old Password', [validators.Required()])
    password = PasswordField('New Password', [validators.Required(), \
                             validators.EqualTo('password2', \
                             message='Passwords must match')])
    password2 = PasswordField('Repeat New Password', [validators.Required()])
    
    def validate_old_password(form, field):
        request = get_current_request()
        if not AuthUser.check_password(id=authenticated_userid(request), \
                                       password=field.data):
            raise ValidationError('Your old password doesn\'t match')

class LoginForm(ExtendedForm):
    username = TextField('Username', validators=[validators.Required()])
    password = PasswordField('Password', validators=[validators.Required()])
    
    def clean(self): 
        errors = [] 
        if not AuthUser.check_password(username=self.data.get('username'), \
                                       password=self.data.get('password')):
            errors.append('Login Error -- please try again')
        return errors


class OAuthForm(ExtendedForm):
    end_point = HiddenField('')
    csrf_token = HiddenField('')

class OpenIdLogin(OAuthForm):
    provider_name = 'openid'

    openid_identifier = TextField('OpenID Identifier')

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
