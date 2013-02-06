import os
import unittest
from sqlalchemy import engine_from_config
from pyramid import testing
from sqlalchemy.orm import sessionmaker
from apex.models import DBSession
from apex.models import Base
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

        cls.Session = sessionmaker()

    @classmethod
    def tearDownClass(cls):
        DBSession.close()
        from apex.models import Base
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('home', '/')
        self.config.add_settings(settings)
        self.config.include('apex')

        connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        DBSession.configure(bind=connection)
        self.session = self.Session(bind=connection)

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
