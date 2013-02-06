import unittest

from pyramid import testing

class Test_lib_libapex(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    #def tearDown(self):
    #    testing.tearDown()

    def test_apexid_from_token(self):
        # apexid_from_token(request)
        pass

    def test_groupfinder(self):
        # groupfinder(userid, request)
        pass

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
        from apex.lib.libapex import apex_settings

        self.assertEqual([], apex_settings(key=None, default=None))
        self.assertEqual('session_secret', \
            apex_settings(key='session_secret', default=None))
        self.assertEqual('home', apex_settings(key='came_from_route', \
            default=None))
        self.assertEqual(None, apex_settings(key='no_match', default=None))

    def test_create_user(self):
        # create_user(**kwargs)
        from apex.lib.libapex import create_user

        #create_user(username='libtest', password='password')
        pass

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
