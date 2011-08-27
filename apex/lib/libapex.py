try:
    import json
except ImportError:
    import simplejson as json

import urlparse

import velruse.store.sqlstore
from velruse.app import parse_config_file
from velruse.store.sqlstore import KeyStorage

from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import remember
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_url
from pyramid.util import DottedNameResolver

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from apex.models import DBSession
from apex.models import AuthUser
from apex.models import AuthGroup
from apex.models import AuthUserLog
from apex.forms import OpenIdLogin
from apex.forms import GoogleLogin
from apex.forms import FacebookLogin
from apex.forms import YahooLogin
from apex.forms import WindowsLiveLogin
from apex.forms import TwitterLogin

auth_provider = {
    'G':'Google',
    'F':'Facebook',
    'T':'Twitter',
    'Y':'Yahoo',
    'O':'OpenID',
    'M':'Microsoft Live',
}

def apexid_from_url(provider, identifier):
    """
    returns the login ID for apex
    """
    id = None
    if provider == 'Google':
        try:
            id = '$G$%s' % \
                 urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]
        except KeyError:
            pass
    elif provider == 'Facebook':
        path = urlparse.urlparse(identifier).path[1:]
        if path:
            try:
                id = '$F$%s' % path
            except:
                pass
    elif provider == 'Twitter':
        try:
            id = '$T$%s' % \
                 urlparse.parse_qs(urlparse.urlparse(identifier).query) \
                     ['id'][0].split('\'')[1]
        except KeyError:
            pass
    elif provider == 'Yahoo':
        urlparts = urlparse.urlparse(identifier)        
        try:
            id = '$Y$%s#%s' % \
                 (urlparts.path.split('/')[2], urlparts.fragment)
        except:
            pass
    elif provider == "OpenID":
        id = '$O$%s' % identifier
    return id

def apexid_from_token(token):
    """ Returns the apex id from the OpenID Token
    """
    dbsession = DBSession()
    auth = json.loads(dbsession.query(KeyStorage.value). \
                      filter(KeyStorage.key==token).one()[0])
    if 'profile' in auth:
        id = apexid_from_url(auth['profile']['providerName'], \
                             auth['profile']['identifier'])
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
    apex_email(request, email, _('Password reset request received'), \
    """
A request to reset your password has been received. Please go to 
the following URL to change your password:

%s

If you did not make this request, you can safely ignore it.
    """ % route_url('apex_reset', request, user_id=user_id, hmac=hmac))

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
    """Usage: create_user(username='test', password='my_password', group='group')
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

def generate_velruse_forms(request, came_from):
    """ Generates variable form based on OpenID providers supported in
    the CONFIG.yaml file
    """
    velruse_forms = []
    if apex_settings('velruse_config'):
        configs = parse_config_file(apex_settings('velruse_config'))[0].keys()
        if apex_settings('provider_exclude'):
            for provider in apex_settings('provider_exclude').split(','):
                if provider.strip() in configs:
                    configs.remove(provider.strip())
        for provider in configs:
            if provider_forms.has_key(provider):
                velruse_forms.append(provider_forms[provider](
                    end_point='%s?csrf_token=%s&came_from=%s' % \
                     (request.route_url('apex_callback'), \
                      request.session.get_csrf_token(),
                      came_from), \
                     csrf_token = request.session.get_csrf_token()
                ))
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
