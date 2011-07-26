"""
id, login, password, display_name, email
"""
import json
import urlparse

import velruse.store.sqlstore
from velruse.store.sqlstore import KeyStorage

from pyrapex.models import DBSession

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

def apex_callback(request):
    auth = apexid_from_token(request.POST['token'])
    return {'req':request, 'auth':auth}
