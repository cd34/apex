try:
    import json
except ImportError:
    import simplejson as json

import requests
from sqlalchemy.orm.exc import NoResultFound

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import Allow
from pyramid.security import authenticated_userid
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import remember
from pyramid.settings import asbool
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_url
from pyramid.util import DottedNameResolver

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from apex import MessageFactory as _
from apex.forms import (OpenIdLogin,
                        GoogleLogin,
                        FacebookLogin,
                        YahooLogin,
                        WindowsLiveLogin,
                        TwitterLogin,
                        BitbucketLogin,
                        GithubLogin,
                        LastfmLogin,
                        IdenticaLogin,
                        LinkedinLogin)
from apex.models import DBSession
from apex.models import AuthID
from apex.models import AuthUser
from apex.models import AuthGroup
from apex.models import AuthUserLog

class EmailMessageText(object):
    """ Default email message text class
    """

    def forgot(self):
        """
In the message body, %_url_% is replaced with:

::

    route_url('apex_reset', request, user_id=user_id, hmac=hmac))
        """
        return {
                'subject': _('Password reset request received'),
                'body': _("""
A request to reset your password has been received. Please go to
the following URL to change your password:

%_url_%

If you did not make this request, you can safely ignore it.
"""),
        }

    def activate(self):
        """
In the message body, %_url_% is replaced with:

::

    route_url('apex_activate', request, user_id=user_id, hmac=hmac))
        """
        return {
                'subject': _('Account activation. Please activate your account.'),
                'body': _("""
This site requires account validation. Please follow the link below to
activate your account:

%_url_%

If you did not make this request, you can safely ignore it.
"""),
        }

def apexid_from_token(request):
    """ Returns the apex id from the OpenID Token
    """
    dbsession = DBSession()
    payload = {'format': 'json', 'token': request.POST['token']}
    velruse = requests.get(request.host_url + '/velruse/auth_info', \
        params=payload)
    if velruse.status_code == 200:
        auth = velruse.json
        if 'profile' in auth:
            auth['id'] = auth['profile']['accounts'][0]['userid']
            auth['provider'] = auth['profile']['accounts'][0]['domain']
            return auth
        return None
    else:
        raise HTTPBadRequest(_('Velruse backing store unavailable'))

def groupfinder(userid, request):
    """ Returns ACL formatted list of groups for the userid in the
    current request
    """
    auth = AuthID.get_by_id(userid)
    if auth:
        return [('group:%s' % group.name) for group in auth.groups]

class RootFactory(object):
    """ Defines the default ACLs, groups populated from SQLAlchemy.
    """
    def __init__(self, request):
        if request.matchdict:
            self.__dict__.update(request.matchdict)

    @property
    def __acl__(self):
        dbsession = DBSession()
        groups = dbsession.query(AuthGroup.name).all()
        defaultlist = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'authenticated'),]
        for g in groups:
            defaultlist.append( (Allow, 'group:%s' % g, g[0]) )
        return defaultlist

provider_forms = {
    'openid': OpenIdLogin,
    'google': GoogleLogin,
    'twitter': TwitterLogin,
    'yahoo': YahooLogin,
    'live': WindowsLiveLogin,
    'facebook': FacebookLogin,
    'bitbucket': BitbucketLogin,
    'github': GithubLogin,
    'identica': IdenticaLogin,
    'lastfm': LastfmLogin,
    'linkedin': LinkedinLogin,
}

def apex_email(request, recipients, subject, body, sender=None):
    """ Sends email message
    """
    mailer = get_mailer(request)
    if not sender:
        sender = apex_settings('sender_email')
        if not sender:
            sender = 'nobody@example.com'
    message = Message(subject=subject,
                  sender=sender,
                  recipients=[recipients],
                  body=body)
    mailer.send(message)

def apex_email_forgot(request, user_id, email, hmac):
    message_class_name = get_module(apex_settings('email_message_text', \
                             'apex.lib.libapex.EmailMessageText'))
    message_class = message_class_name()
    message_text = getattr(message_class, 'forgot')()

    message_body = message_text['body'].replace('%_url_%', \
        route_url('apex_reset', request, user_id=user_id, hmac=hmac))

    apex_email(request, email, message_text['subject'], message_body)

def apex_email_activate(request, user_id, email, hmac):
    message_class_name = get_module(apex_settings('email_message_text', \
                             'apex.lib.libapex.EmailMessageText'))
    message_class = message_class_name()
    message_text = getattr(message_class, 'activate')()

    message_body = message_text['body'].replace('%_url_%', \
        route_url('apex_activate', request, user_id=user_id, hmac=hmac))

    apex_email(request, email, message_text['subject'], message_body)

def apex_settings(key=None, default=None):
    """ Gets an apex setting if the key is set.
        If no key it set, returns all the apex settings.

        Some settings have issue with a Nonetype value error,
        you can set the default to fix this issue.
    """
    settings = get_current_registry().settings

    if key:
        return settings.get('apex.%s' % key, default)
    else:
        apex_settings = []
        for k, v in settings.items():
            if k.startswith('apex.'):
                apex_settings.append({k.split('.')[1]: v})

        return apex_settings

def create_user(**kwargs):
    """

::

    from apex.lib.libapex import create_user

    create_user(username='test', password='my_password', active='Y')

    Optional Parameters:

    display_name
    group



    Returns: AuthID object
    """
    auth_id = AuthID(active=kwargs.get('active', 'Y'))
    if 'display_name' in kwargs:
        user.display_name = kwargs['display_name']
        del kwargs['display_name']

    user = AuthUser(login=kwargs['username'], password=kwargs['password'], \
               active=kwargs.get('active', 'Y'))
    auth_id.users.append(user)

    if 'group' in kwargs:
        try:
            group = DBSession.query(AuthGroup). \
            filter(AuthGroup.name==kwargs['group']).one()

            auth_id.groups.append(group)
        except NoResultFound:
            pass

        del kwargs['group']

    for key, value in kwargs.items():
        setattr(user, key, value)

    DBSession.add(user)
    DBSession.flush()
    return user

def generate_velruse_forms(request, came_from):
    """ Generates variable form based on OpenID providers supported in
    the CONFIG.yaml file
    """
    velruse_forms = []
    providers = apex_settings('velruse_providers', None)
    if providers:
        providers = [x.strip() for x in providers.split(',')]
        for provider in providers:
            if provider_forms.has_key(provider):
                form = provider_forms[provider](
                    end_point='%s?csrf_token=%s&came_from=%s' % \
                     (request.route_url('apex_callback'), \
                      request.session.get_csrf_token(),
                      came_from), \
                     csrf_token = request.session.get_csrf_token(),
                )
                velruse_forms.append(form)
    return velruse_forms

def get_module(package):
    """ Returns a module based on the string passed
    """
    resolver = DottedNameResolver(package.split('.', 1)[0])
    return resolver.resolve(package)

def apex_remember(request, user, max_age=None):
    if asbool(apex_settings('log_logins')):
        if apex_settings('log_login_header'):
            ip_addr = request.environ.get(apex_settings('log_login_header'), \
                    u'invalid value - apex.log_login_header')
        else:
             ip_addr = unicode(request.environ['REMOTE_ADDR'])
        record = AuthUserLog(auth_id=user.auth_id, user_id=user.id, \
            ip_addr=ip_addr)
        DBSession.add(record)
        DBSession.flush()
    return remember(request, user.auth_id, max_age=max_age)

def get_came_from(request):
    return request.GET.get('came_from',
                           request.POST.get(
                               'came_from',
                               route_url(apex_settings('came_from_route'), request))
                          )

class RequestFactory(Request):
    """ Custom Request factory, that adds the user context
        to request.

        http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/authentication.html
    """
    @reify
    def user(self):
        user = None
        if authenticated_userid(self):
            user = AuthID.get_by_id(authenticated_userid(self))
        return user
