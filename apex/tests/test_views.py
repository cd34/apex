import os
import webob.multidict

from pyramid import testing

from apex.tests import BaseTestCase

here = os.path.abspath(os.path.dirname(__file__))

""" added to provide dummy environment to prevent exception when
hostname isn't defined.
"""
environ = {
    'HTTP_HOST':'test.com',
    'SERVER_NAME':'test.com',
}


class Test_views(BaseTestCase):
    def test_view_login(self):
        from apex.lib.libapex import create_user
        from apex.views import login

        create_user(username='test', password='password')

        request = testing.DummyRequest()

        # wtforms requires this
        request.POST = webob.multidict.MultiDict()
        request.context = testing.DummyResource()
        response = login(request)

        self.assertEqual(response['title'], 'You need to login')

    def test_simple_login(self):
        from apex.lib.libapex import create_user
        from apex.views import login

        create_user(username='test', password='password')

        request = testing.DummyRequest(environ=environ)
        request.method = 'POST'
        # wtforms requires this
        request.POST = webob.multidict.MultiDict()
        request.POST['username'] = 'test'
        request.POST['password'] = 'password'

        request.context = testing.DummyResource()
        response = login(request)

        # response object from dummy missing status_int
        #self.assertEqual(response.status_int, 302)

    def test_fail_login(self):
        from apex.lib.libapex import create_user
        from apex.views import login

        create_user(username='test', password='password1')

        request = testing.DummyRequest(environ=environ)
        request.method = 'POST'
        # wtforms requires this
        request.POST = webob.multidict.MultiDict()
        request.POST['username'] = 'test'
        request.POST['password'] = 'password'

        request.context = testing.DummyResource()
        response = login(request)

        self.assertEqual(len(response['form'].errors), 1)

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

