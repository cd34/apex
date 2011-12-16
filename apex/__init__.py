from pyramid_mailer.interfaces import IMailer

from apex.i18n import MessageFactory

from sqlalchemy import engine_from_config

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import ISessionFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.settings import asbool
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import Forbidden

from apex.exceptions import ApexAuthSecret
from apex.exceptions import ApexSessionSecret
from apex.interfaces import IApex
from apex.interfaces import ApexImplementation
from apex.lib.libapex import groupfinder
from apex.lib.libapex import RequestFactory
from apex.lib.libapex import RootFactory
from apex.models import DBSession
from apex.views import apex_callback
from apex.views import activate
from apex.views import change_password
from apex.views import edit
from apex.views import login
from apex.views import logout
from apex.views import forgot_password
from apex.views import forbidden
from apex.views import openid_required
from apex.views import register
from apex.views import reset_password

"""
    Allows flash messages to be called as:
::
    from apex import flash

"""


from apex.lib.flash import flash

def includeme(config):
    settings = config.registry.settings
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    #initialize_sql(engine_from_config(settings, 'sqlalchemy.'), settings)

    config.registry.registerUtility(ApexImplementation, IApex)
    config.add_translation_dirs('apex:locale/')

    if not config.registry.queryUtility(ISessionFactory):
        if not settings.has_key('apex.session_secret'):
            raise ApexSessionSecret()

        config.set_session_factory( \
               UnencryptedCookieSessionFactoryConfig( \
               settings.get('apex.session_secret')))

    if not config.registry.queryUtility(IAuthorizationPolicy):
        authz_policy = ACLAuthorizationPolicy()
        config.set_authorization_policy(authz_policy)


    if not config.registry.queryUtility(IAuthenticationPolicy):
        if not settings.has_key('apex.auth_secret'):
            raise ApexAuthSecret()
        authn_policy = AuthTktAuthenticationPolicy( \
                       settings.get('apex.auth_secret'), \
                       callback=groupfinder)
        config.set_authentication_policy(authn_policy)

    cache = RootFactory.__acl__
    config.set_root_factory(RootFactory)
    
    use_request_factory = asbool(settings.get('apex.use_request_factory', True))
    if use_request_factory:
        config.set_request_factory(RequestFactory)

    if not config.registry.queryUtility(IMailer):
        config.include('pyramid_mailer')

    if not settings.get('mako.directories'):
        config.add_settings({'mako.directories': ['apex:templates']})

    config.add_subscriber('apex.lib.subscribers.csrf_validation',
                          'pyramid.events.ContextFound')
    config.add_subscriber('apex.lib.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')

    config.add_static_view('apex/static', 'apex:static')

    config.add_view(forbidden, context=Forbidden)

    render_template = settings['apex.apex_render_template'
                              ] = settings.get('apex.apex_template',
                                               'apex:templates/apex_template.mako')

    config.add_route('apex_login', '/login')
    config.add_view(login, route_name='apex_login',
                    renderer=render_template)

    config.add_route('apex_logout', '/logout')
    config.add_view(logout, route_name='apex_logout',
                    renderer=render_template)

    config.add_route('apex_register', '/register')
    config.add_view(register, route_name='apex_register',
                    renderer=render_template)

    config.add_route('apex_password', '/password')
    config.add_view(change_password, route_name='apex_password',
                    renderer=render_template, permission='authenticated')

    config.add_route('apex_forgot', '/forgot')
    config.add_view(forgot_password, route_name='apex_forgot',
                    renderer=render_template)

    config.add_route('apex_reset', '/reset/:user_id/:hmac')
    config.add_view(reset_password, route_name='apex_reset',
                    renderer=render_template)

    config.add_route('apex_activate', '/activate/:user_id/:hmac')
    config.add_view(activate, route_name='apex_activate',
                    renderer=render_template)

    config.add_route('apex_callback', '/apex_callback')
    config.add_view(apex_callback, route_name='apex_callback')

    config.add_route('apex_openid_required', '/openid_required')
    config.add_view(openid_required, route_name= \
                    'apex_openid_required', \
                    renderer=render_template)

    if settings.has_key('apex.auth_profile'):
        use_edit = asbool(settings.get('apex.use_apex_edit', False))
        if use_edit:
            config.add_route('apex_edit', '/edit')
            config.add_view(edit, route_name='apex_edit', \
                            renderer=render_template, \
                            permission='authenticated')
