import unittest

from pyramid import testing
from apex.tests import BaseTestCase


class Test_lib_libapex(BaseTestCase):
    def test_apex_id_from_token(self):
        # apex_id_from_token(request)
        pass

    def test_groupfinder(self):
        # groupfinder(userid, request)
        from apex.lib.libapex import (create_user,
                                      groupfinder)

        user = create_user(username='libtest', password='password', \
            group='users')
        self.assertEqual([u'group:users'], groupfinder(user.auth_id, None))
        self.assertNotEqual(None, groupfinder(user.auth_id, None))
        self.assertEqual(None, groupfinder(18, None))
        self.assertNotEqual([u'group:users'], groupfinder(18, None))

    def test_apex_email(self):
        # apex_email(request, recipients, subject, body, sender=None)
        pass

    def test_apex_email_forgot(self):
        # apex_email_forgot(request, user_id, email, hmac)
        pass

    def test_apex_email_activate(self):
        # apex_email_activate(request, user_id, email, hmac)
        pass

    def test_apex_settings(self):
        # apex_settings(key=None, default=None)
        # settings not being set in registry
        from apex.lib.libapex import apex_settings

        """
        self.assertEqual([], apex_settings(key=None, default=None))
        depends on registry which isn't being passed

        self.assertEqual('session_secret', \
            apex_settings(key='session_secret', default=None))
        self.assertEqual('home', apex_settings(key='came_from_route', \
            default=None))
        self.assertEqual(None, apex_settings(key='no_match', default=None))
        """

    def test_create_user(self):
        # create_user(**kwargs)
        from apex.lib.libapex import create_user
        from apex.models import (AuthUser,
                                 DBSession)

        create_user(username='libtest', password='password')
        # check that auth_id, auth_user, auth_group are added
        self.assertEqual('libtest', DBSession.query(AuthUser.login). \
            filter(AuthUser.login=='libtest').one()[0])

    def test_generate_velruse_forms(self):
        # generate_velruse_forms(request, came_from)
        pass

    def test_get_module(self):
        # get_module(package)
        pass

    def test_apex_remember(self):
        # apex_remember(request, user, max_age=None)
        pass

    def test_get_came_from(self):
        # get_came_from(request)
        pass
