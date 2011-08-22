"""
initial test issue due to fact that we're not testing an app, but an include
"""
import os
import unittest
from pyramid import testing

here = os.path.abspath(os.path.dirname(__file__))

environ = {
    'HTTP_HOST':'test.com',
    'SERVER_NAME':'test.com',
}

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
        import apex
        self.config = testing.setUp()
        self.config.add_route('home', '/')
        self.config.add_settings(settings)
        self.config.include('apex')

    def tearDown(self):
        testing.tearDown()

    def test_logout(self):
        from apex.views import logout
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        response = logout(request)

        self.assertEqual('302 Found', response.status)
