__init__.py
===========

::

    from pyramid.config import Configurator
    from sqlalchemy import engine_from_config

    from apex_example.models import initialize_sql

    def main(global_config, **settings):
        """ This function returns a Pyramid WSGI application.
        """
        engine = engine_from_config(settings, 'sqlalchemy.')
        initialize_sql(engine)
        config = Configurator(settings=settings)

        """ Set up the minimum routes for our example.
        """
        config.add_route('home', '/')
        config.add_route('test', '/test')
        config.add_route('protected', '/protected')
        config.add_route('groupusers', '/groupusers')

        """ Must include this line
        """
        config.include('apex')

        """ Use the newer method for settings views/permissions
        """
        config.scan()

        return config.make_wsgi_app()
