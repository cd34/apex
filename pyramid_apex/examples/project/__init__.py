from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyrapex.lib.login import forbidden_view, groupfinder
from pyramid.exceptions import Forbidden

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyrapex.models import initialize_sql

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'pyrapex:static')
    config.add_route('home', '/')
    config.add_view('pyrapex.views.index', route_name='home',
                    renderer='index.mako')

    config.add_route('protected', '/protected')
    config.add_view('pyrapex.views.protected', route_name='protected',
                    renderer='protected.mako', permission='authenticated')

    config.add_route('test', '/test')
    config.add_view('pyrapex.views.test', route_name='test',
                    renderer='test.mako')

    config.include('pyramid_apex')

    return config.make_wsgi_app()

