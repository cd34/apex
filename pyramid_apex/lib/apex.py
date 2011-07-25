"""
id, login, password, display_name, email
"""
import json
import urlparse

import velruse.store.sqlstore
from velruse.store.sqlstore import KeyStorage

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Allow
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.url import current_route_url
from pyramid.url import route_url

from pyramid_apex.models import DBSession
from pyramid_apex.models import AuthUser

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
             urlparse.parse_qs(urlparse.urlparse(identifier).query)['id'][0]
    if provider == 'Yahoo':
        urlparts = urlparse.urlparse(identifier)        
        id = '$Y$%s#%s' % \
             (urlparts.path.split('/')[2], urlparts.fragment)
    return id

def apexid_from_token(token):
    dbsession = DBSession()
    auth = json.loads(dbsession.query(KeyStorage.value). \
                      filter(KeyStorage.key==token).one()[0])
    id = apexid_from_url(auth['profile']['providerName'], \
                         auth['profile']['identifier'])
    auth['apexid'] = id
    return auth

def groupfinder(userid, request):
    dbsession = DBSession()
    auth = dbsession.query(AuthUser).filter(AuthUser.id==userid).first()
    if auth:
        return [('group:%s' % group.name) for group in auth.groups]

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'authenticated'),
                (Allow, 'group:user', 'user'),
                (Allow, 'group:admin', 'admin') ]
    def __init__(self, request):
        if request.matchdict:
            self.__dict__.update(request.matchdict)

def forbidden_view(request):
    return HTTPFound(location = '%s?came_from=%s' %
                                (route_url('pyramid_apex_login', request),
                                 current_route_url(request)) )
