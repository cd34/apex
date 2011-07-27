"""
id, login, password, display_name, email
"""
try:
    import json
except ImportError:
    import simplejson as json

import urlparse

import velruse.store.sqlstore
from velruse.store.sqlstore import KeyStorage

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated

from pyramid_apex.models import DBSession
from pyramid_apex.models import AuthUser
from pyramid_apex.models import AuthGroup

from pyramid_apex.forms import OpenIdLogin
from pyramid_apex.forms import GoogleLogin
from pyramid_apex.forms import FacebookLogin
from pyramid_apex.forms import YahooLogin
from pyramid_apex.forms import WindowsLiveLogin
from pyramid_apex.forms import TwitterLogin

def apexid_from_url(provider, identifier):
    id = None
    if provider == 'Google':
        id = '$G$%s' % \
             urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]
    if provider == 'Facebook':
        id = '$F$%s' % \
             urlparse.urlparse(identifier).path[1:]
    if provider == 'Twitter':
        id = '$T$%s' % \
             urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]. \
                               split('\'')[1]
    if provider == 'Yahoo':
        urlparts = urlparse.urlparse(identifier)        
        id = '$Y$%s#%s' % \
             (urlparts.path.split('/')[2], urlparts.fragment)
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
