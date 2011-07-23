from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy, ISessionFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from zope.component import getUtility

from sqlalchemy import engine_from_config

from pyramid_apex.exceptions import ApexSessionSecret
from pyramid_apex.views import login, logout, change_password, forgot_password, register
from pyramid_apex.models import initialize_sql

def includeme(config):
    settings = config.registry.settings

    initialize_sql(engine_from_config(settings, 'sqlalchemy.'))

    if not config.registry.queryUtility(ISessionFactory):
        if not settings.has_key('apex.session_secret'):
            raise ApexSessionSecret()
        
        config.set_session_factory(UnencryptedCookieSessionFactoryConfig(settings.get('apex.session_secret')))
    
    if not config.registry.queryUtility(IAuthenticationPolicy):
        pass

    if not config.registry.queryUtility(IAuthorizationPolicy):
        pass
    
    config.add_settings({'mako.directories': ['pyramid_apex:templates']})

    config.add_subscriber('pyramid_apex.lib.subscribers.csrf_validation', 'pyramid.events.NewRequest')
    config.add_subscriber('pyramid_apex.lib.subscribers.add_renderer_globals', 'pyramid.events.BeforeRender')

    config.add_route('pyramid_auth_login', '/auth/login')
    config.add_view(login, route_name='pyramid_auth_login', renderer='auth_template.mako')
    
    config.add_route('pyramid_auth_logout', '/auth/logout')
    config.add_view(logout, route_name='pyramid_auth_logout', renderer='auth_template.mako')

    config.add_route('pyramid_auth_register', '/auth/register')
    config.add_view(register, route_name='pyramid_auth_register', renderer='auth_template.mako')

    config.add_route('pyramid_auth_password', '/auth/password')
    config.add_view(change_password, route_name='pyramid_auth_password', renderer='auth_template.mako')
    
    config.add_route('pyramid_auth_forgot', '/auth/forgot')
    config.add_view(forgot_password, route_name='pyramid_auth_forgot', renderer='auth_template.mako')
    
