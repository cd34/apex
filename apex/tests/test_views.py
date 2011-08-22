import os
import unittest

from sqlalchemy import engine_from_config

from pyramid import testing

here = os.path.abspath(os.path.dirname(__file__))

""" added to provide dummy environment to prevent exception when
hostname isn't defined.
"""
environ = {
    'HTTP_HOST':'test.com',
    'SERVER_NAME':'test.com',
}

""" bare minimum settings required for testing
"""
settings = {
    'sqlalchemy.url':'sqlite:///apex.test.db',
    'mako.directories':'{0}/../apex/templates'.format(here),
    'apex.session_secret':'session_secret',
    'apex.auth_secret':'auth_secret',
    'apex.came_from_route':'home',
    'apex.velruse_config':'{0}/CONFIG.yaml',
}

class Test_views(unittest.TestCase):
    def setUp(self):
        """ must add default route 'home' and include apex
            we also must create a default user/pass/group to test
        """
        import apex
        from apex.lib.libapex import create_user
        self.engine = engine_from_config(settings, 'sqlalchemy.')
        self.config = testing.setUp()
        self.config.add_route('home', '/')
        self.config.add_settings(settings)
        self.config.include('apex')

        """ creating user for later testing
        create_user(username='test', password='password')
        """

    def tearDown(self):
        """ import Base so that we can drop the tables after each test
        """
        from apex.models import Base
        testing.tearDown()
        Base.metadata.drop_all(self.engine)

    def test_login(self):
        pass
        """ requires REMOTE_ADDR
        from apex.views import login
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        response = login(request)

        self.assertEqual('302 Found', response.status)
        """

    def test_logout(self):
        """ need to import environ for SERVER_NAME and HOST_NAME
        since we're dealing with cookies.
        """
        from apex.views import logout
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        response = logout(request)

        self.assertEqual('302 Found', response.status)

    def test_change_password(self):
        pass

    def test_forgot_password(self):
        pass

    def test_reset_password(self):
        pass

    def test_register(self):
        pass

    def test_apex_callback(self):
        pass

