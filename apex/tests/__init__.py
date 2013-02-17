import os
import unittest
from sqlalchemy import engine_from_config
from pyramid import testing
from apex.models import (Base,
                         DBSession)
here = os.path.abspath(os.path.dirname(__file__))


""" bare minimum settings required for testing
"""
settings = {
    'sqlalchemy.url':'sqlite:///apex.test.db',
    'mako.directories':'{0}/../apex/templates'.format(here),
    'apex.session_secret':'session_secret',
    'apex.auth_secret':'auth_secret',
    'apex.came_from_route':'home',
    'apex.use_recaptcha_on_login': 'false',
}


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ must add default route 'home' and include apex
            we also must create a default user/pass/group to test
        """
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        DBSession.configure(bind=cls.engine)
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        DBSession.close()
        #Base.metadata.drop_all(cls.engine)

    def setUp(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)

        self.config.add_route('home', '/')
        self.config.add_settings(settings)
        self.config.include('apex')

    def tearDown(self):
        testing.tearDown()
