import apex.lib.libapex

from wtforms import (HiddenField,
                     PasswordField,
                     TextField,
                     validators)

from apex import MessageFactory as _
from pyramid.security import authenticated_userid
from pyramid.threadlocal import (get_current_registry,
                                 get_current_request)
from pyramid.settings import asbool

from apex.models import (AuthGroup,
                         AuthID,
                         AuthUser,
                         DBSession)
from apex.lib.form import ExtendedForm

class RegisterForm(ExtendedForm):
    """ Registration Form
    """
    login = TextField(_('Username'), [validators.Required(), \
                         validators.Length(min=4, max=25)])
    password = PasswordField(_('Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat Password'), [validators.Required()])
    email = TextField(_('Email Address'), [validators.Required(), \
                      validators.Email()])

    def validate_login(form, field):
        if AuthUser.get_by_login(field.data) is not None:
            raise validators.ValidationError(_('Sorry that username already exists.'))

    def create_user(self, login):
        group = self.request.registry.settings.get('apex.default_user_group',
                                                   None)
        if asbool(apex.lib.libapex.apex_settings('email_validate')):
            activate='Y'
        else:
            activate='N'

        user = apex.lib.libapex.create_user(username=login,
                                            password=self.data['password'],
                                            email=self.data['email'],
                                            group=group,
                                            activate=activate)
        return user

    def save(self):
        new_user = self.create_user(self.data['login'])
        self.after_signup(user=new_user)

        return new_user

    def after_signup(self, **kwargs):
        """ Function to be overloaded and called after form submission
        to allow you the ability to save additional form data or perform
        extra actions after the form submission.
        """
        pass

class ChangePasswordForm(ExtendedForm):
    """ Change Password Form
    """
    user_id = HiddenField('')
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
    login = TextField(_('Username'), validators=[validators.Required()])
    password = PasswordField(_('Password'), validators=[validators.Required()])

    def clean(self):
        errors = []
        if not AuthUser.check_password(login=self.data.get('login'), \
                                       password=self.data.get('password')):
            errors.append(_('Login Error -- please try again'))
        return errors

class ForgotForm(ExtendedForm):
    login = TextField(_('Username'), [validators.Optional()])
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
    def validate_login(form, field):
        if AuthUser.get_by_login(field.data) is None:
            raise validators.ValidationError(_('Sorry that username doesn\'t exist.'))

    def validate_email(form, field):
        if AuthUser.get_by_email(field.data) is None:
            raise validators.ValidationError(_('Sorry that email doesn\'t exist.'))

    def clean(self):
        errors = []
        if not self.data.get('login') and not self.data.get('email'):
            errors.append(_('You need to specify either a Username or ' \
                            'Email address'))
        return errors

class ResetPasswordForm(ExtendedForm):
    password = PasswordField(_('New Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat New Password'), [validators.Required()])

class AddAuthForm(ExtendedForm):
    login = TextField(_('Username'), [validators.Required(), \
                         validators.Length(min=4, max=25)])
    password = PasswordField(_('Password'), [validators.Required(), \
                             validators.EqualTo('password2', \
                             message=_('Passwords must match'))])
    password2 = PasswordField(_('Repeat Password'), [validators.Required()])
    email = TextField(_('Email Address'), [validators.Required(), \
                      validators.Email()])

    def validate_login(form, field):
        if AuthUser.get_by_login(field.data) is not None:
            raise validators.ValidationError(_('Sorry that username already exists.'))

    def create_user(self, auth_id, login):
        id = DBSession.query(AuthID).filter(AuthID.id==auth_id).one()
        user = AuthUser(
            login=login,
            password=self.data['password'],
            email=self.data['email'],
        )
        id.users.append(user)
        DBSession.add(user)
        DBSession.flush()

        return user

    def save(self, auth_id):
        new_user = self.create_user(auth_id, self.data['login'])
        self.after_signup(user=new_user)

    def after_signup(self, **kwargs):
        """ Function to be overloaded and called after form submission
        to allow you the ability to save additional form data or perform
        extra actions after the form submission.
        """
        pass

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

class BitbucketLogin(OAuthForm):
    provider_name = 'bitbucket'
    provider_proper_name = 'Bitbucket'

class GithubLogin(OAuthForm):
    provider_name = 'github'
    provider_proper_name = 'Github'

class IdenticaLogin(OAuthForm):
    provider_name = 'identica'
    provider_proper_name = 'Identi.ca'

class LastfmLogin(OAuthForm):
    provider_name = 'lastfm'
    provider_proper_name = 'Last.fm'

class LinkedinLogin(OAuthForm):
    provider_name = 'linkedin'
    provider_proper_name = 'LinkedIn'

class OpenIDRequiredForm(ExtendedForm):
    pass
