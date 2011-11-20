try:
    import json
except ImportError:
    import simplejson as json

import urlparse
import logging
import urllib2

import velruse.store.sqlstore
from velruse.store.sqlstore import KeyStorage

from sqlalchemy.orm.exc import NoResultFound

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
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
from apex.forms import OpenIdLogin
from apex.forms import GoogleLogin
from apex.forms import FacebookLogin
from apex.forms import GithubLogin
from apex.forms import YahooLogin
from apex.forms import WindowsLiveLogin
from apex.forms import TwitterLogin
from apex.models import DBSession
from apex.models import AuthUser
from apex.models import AuthGroup
from apex.models import AuthUserLog

auth_provider = {
    'G':'Google',
    'H':'Github',
    'F':'Facebook',
    'T':'Twitter',
    'Y':'Yahoo',
    'O':'OpenID',
    'M':'Microsoft Live',
}

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

def apexid_from_url(provider, identifier):
    """
    returns the login ID for apex
    """
    id = identifier
    providers = [a['domain'] for a in provider]
    provider = ''
    if providers:
        provider = providers[0].lower()
        id = "%s > %s" % (provider, id)
    return id

def apexid_from_token(token):
    """ Returns the apex id from the OpenID Token
    """
    dbsession = DBSession()
    auth = json.loads(dbsession.query(KeyStorage.value). \
                      filter(KeyStorage.key==token).one()[0])
    if 'profile' in auth:
        pr = auth['profile']
        name = pr.get('displayName', '')
        auth['name'] = name
        if not name or ('twitter' in pr['accounts'][0]['domain']):
            if not name:
                auth['name'] =  pr['accounts'][0]['userid'] 
            name = pr['accounts'][0]['userid']
        id = apexid_from_url(pr['accounts'], name)
        auth['apexid'] = id
        return auth
    return None

def groupfinder(userid, request):
    """ Returns ACL formatted list of groups for the userid in the
    current request
    """
    auth = AuthUser.get_by_id(userid)
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
    'github': GithubLogin,
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

    create_user(username='test', password='my_password', active='Y', group='group')

    Returns: AuthUser object
    """
    user = AuthUser()

    if 'group' in kwargs:
        try:
            group = DBSession.query(AuthGroup). \
            filter(AuthGroup.name==kwargs['group']).one()

            user.groups.append(group)
        except NoResultFound:
            pass

        del kwargs['group']

    for key, value in kwargs.items():
        setattr(user, key, value)

    DBSession.add(user)
    DBSession.flush()
    return user

def query_velruse_host(query):
    vurl = apex_settings('velruse_url')
    auth_url = '%s/%s' %( vurl, query)
    req = urllib2.Request(auth_url, None, {'user-agent':'auth/apex'})
    configs = json.loads(urllib2.urlopen(req).read())
    return configs

def generate_velruse_forms(request, came_from):
    """ Generates variable form based on OpenID providers
    offered by the velruse backend.
    XXX: If the method is too heavy, please cache it a while.
    """
    velruse_forms = []
    logger = logging.getLogger('apex.generate_velruse_forms')
    configs = {}
    try:
        configs = query_velruse_host('auth_providers_list')
    except Exception, e:
        logger.error('Error while gettings providers from velruse: %s' % e)
    if apex_settings('provider_exclude'):
        for provider in apex_settings('provider_exclude').split(','):
            if provider.strip() in configs:
                configs.remove(provider.strip())
    for vprovider in configs:
        provider = vprovider.replace(
            'velruse.', '').replace('providers.', '')
        infos = configs[vprovider]
        if provider_forms.has_key(provider):
            form = provider_forms[provider](
                end_point='%s?csrf_token=%s&came_from=%s' % \
                 (request.route_url('apex_callback'), \
                  request.session.get_csrf_token(),
                  came_from), \
                 csrf_token = request.session.get_csrf_token(),
            )
            keys = ['process', 'login']
            for key in keys:
                if key in infos:
                    setattr(form, 'velruse_%s' % key, infos[key])
            if provider == 'facebook':
                form.scope.data = apex_settings('velruse_facebook_scope')

            velruse_forms.append(form)
    return velruse_forms

def get_module(package):
    """ Returns a module based on the string passed
    """
    resolver = DottedNameResolver(package.split('.', 1)[0])
    return resolver.resolve(package)

def apex_remember(request, user_id):
    if asbool(apex_settings('log_logins')):
        if apex_settings('log_login_header'):
            ip_addr=request.environ.get(apex_settings('log_login_header'), \
                    u'invalid value - apex.log_login_header')
        else:
             ip_addr=request.environ['REMOTE_ADDR']
        record = AuthUserLog(user_id=user_id, ip_addr=ip_addr)
        DBSession.add(record)
        DBSession.flush()
    return remember(request, user_id)

class RequestFactory(Request):
    """ Custom Request factory, that adds the user context
        to request.

        http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/authentication.html
    """
    @reify
    def user(self):
        user = None
        if authenticated_userid(self):
            user = AuthUser.get_by_id(authenticated_userid(self))
        return user
