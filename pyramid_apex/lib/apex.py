try:
    import json
except ImportError:
    import simplejson as json

import urlparse

import velruse.store.sqlstore
from velruse.store.sqlstore import KeyStorage

from sqlalchemy.orm.exc import NoResultFound

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_url

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pyramid_apex.models import DBSession
from pyramid_apex.models import AuthUser
from pyramid_apex.models import AuthGroup
from pyramid_apex.forms import OpenIdLogin
from pyramid_apex.forms import GoogleLogin
from pyramid_apex.forms import FacebookLogin
from pyramid_apex.forms import YahooLogin
from pyramid_apex.forms import WindowsLiveLogin
from pyramid_apex.forms import TwitterLogin

auth_provider = {
    'G':'Google',
    'F':'Facebook',
    'T':'Twitter',
    'Y':'Yahoo',
    'O':'OpenID',
    'M':'Microsoft Live',
}

def apexid_from_url(provider, identifier):
    id = None
    if provider == 'Google':
        id = '$G$%s' % \
             urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]
    elif provider == 'Facebook':
        id = '$F$%s' % \
             urlparse.urlparse(identifier).path[1:]
    elif provider == 'Twitter':
        id = '$T$%s' % \
             urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]. \
                               split('\'')[1]
    elif provider == 'Yahoo':
        urlparts = urlparse.urlparse(identifier)        
        id = '$Y$%s#%s' % \
             (urlparts.path.split('/')[2], urlparts.fragment)
    elif provider == "OpenID":
        id = '$O$%s' % identifier
    return id

def apexid_from_token(token):
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
    auth = AuthUser.get_by_id(userid)
    if auth:
        return [('group:%s' % group.name) for group in auth.groups]

class RootFactory(object):
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
    """ % route_url('pyramid_apex_reset', request, user_id=user_id, hmac=hmac))

def apex_settings(key=None):
    settings = get_current_registry().settings

    if key:
        return settings.get('apex.%s' % key)
    else:
        apex_settings = []
        for k, v in settings.items():
            if k.startswith('apex.'):
                apex_settings.append({k.split('.')[1]: v})

        return apex_settings

def create_user(**kwargs):
    """Usage: create_user(username='test', password='my_password', group='group')
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
