from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import ISessionFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import Forbidden

from zope.component import getUtility

from sqlalchemy import engine_from_config

from pyramid_apex.exceptions import ApexAuthSecret
from pyramid_apex.exceptions import ApexSessionSecret
from pyramid_apex.lib.apex import forbidden_view
from pyramid_apex.lib.apex import groupfinder
from pyramid_apex.lib.apex import RootFactory
from pyramid_apex.models import initialize_sql
from pyramid_apex.views import apex_callback
from pyramid_apex.views import change_password
from pyramid_apex.views import login
from pyramid_apex.views import logout
from pyramid_apex.views import forgot_password
from pyramid_apex.views import register

def includeme(config):
    settings = config.registry.settings

    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))

    if not config.registry.queryUtility(ISessionFactory):
        if not settings.has_key('apex.session_secret'):
            raise ApexSessionSecret()
        
        config.set_session_factory( \
               UnencryptedCookieSessionFactoryConfig( \
               settings.get('apex.session_secret')))

    """ evil stuff, will break one day
    """    
    if not config.registry.queryUtility(IAuthenticationPolicy):
        if not settings.has_key('apex.auth_secret'):
            raise ApexAuthSecret()
        authn_policy = AuthTktAuthenticationPolicy( \
                       settings.get('apex.session_secret'), \
                       callback=groupfinder)
        config._set_authentication_policy(authn_policy)

    if not config.registry.queryUtility(IAuthorizationPolicy):
        authz_policy = ACLAuthorizationPolicy()
        config._set_authorization_policy(authz_policy)

    config._set_root_factory(RootFactory)
    """ end of evil stuff
    """

    if not settings.get('mako.directories'):
        config.add_settings({'mako.directories': ['pyramid_apex:templates']})
    
    config.add_subscriber('pyramid_apex.lib.subscribers.csrf_validation', \
                          'pyramid.events.NewRequest')
    config.add_subscriber('pyramid_apex.lib.subscribers.add_renderer_globals', \
                          'pyramid.events.BeforeRender')

    config.add_view(forbidden_view, context=Forbidden)

    config.add_route('pyramid_apex_login', '/auth/login')
    config.add_view(login, route_name='pyramid_apex_login', \
                    renderer='pyramid_apex:templates/apex_template.mako')
    
    config.add_route('pyramid_apex_logout', '/auth/logout')
    config.add_view(logout, route_name='pyramid_apex_logout', \
                    renderer='pyramid_apex:templates/apex_template.mako')

    config.add_route('pyramid_apex_register', '/auth/register')
    config.add_view(register, route_name='pyramid_apex_register', \
                    renderer='pyramid_apex:templates/apex_template.mako')

    config.add_route('pyramid_apex_password', '/auth/password')
    config.add_view(change_password, route_name='pyramid_apex_password', \
                    renderer='pyramid_apex:templates/apex_template.mako')
    
    config.add_route('pyramid_apex_forgot', '/auth/forgot')
    config.add_view(forgot_password, route_name='pyramid_apex_forgot', \
                    renderer='pyramid_apex:templates/apex_template.mako')
    
    config.add_route('pyramid_apex_callback', '/auth/apex_callback')
    config.add_view(apex_callback, route_name='pyramid_apex_callback')
