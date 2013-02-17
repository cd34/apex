import os
import webob.multidict
import apex.views

from pyramid import testing
from apex.tests import BaseTestCase
from apex.lib.libapex import create_user

here = os.path.abspath(os.path.dirname(__file__))

""" added to provide dummy environment to prevent exception when
hostname isn't defined.
"""
environ = {
    'HTTP_HOST': 'test.com',
    'SERVER_NAME': 'test.com',
    'REMOTE_ADDR': '127.0.0.1',
}


class Test_views(BaseTestCase):
    def test_view_login(self):
        create_user(username='test', password='password')

        request = testing.DummyRequest()

        # wtforms requires this
        request.POST = webob.multidict.MultiDict()
        request.context = testing.DummyResource()
        response = apex.views.login(request)

        self.assertEqual(response['title'], 'You need to login')

    def test_login(self):
        create_user(username='test', password='password')

        request = testing.DummyRequest(environ=environ)
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        request.POST['login'] = 'test'
        request.POST['password'] = 'password'
        request.context = testing.DummyResource()
        response = apex.views.login(request)
        self.assertEqual(response.status, "302 Found")

    def test_fail_login(self):
        create_user(username='test', password='password1')

        request = testing.DummyRequest(environ=environ)
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        request.POST['login'] = 'test'
        request.POST['password'] = 'password'
        request.context = testing.DummyResource()
        response = apex.views.login(request)
        self.assertEqual(len(response['form'].errors), 1)

    def test_logout(self):
        """ need to import environ for SERVER_NAME and HOST_NAME
        since we're dealing with cookies.
        """
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        response = apex.views.logout(request)

        self.assertEqual('302 Found', response.status)

    def test_change_password_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        # no user
        self.assertRaises(AttributeError, apex.views.change_password, request)

    def test_change_password(self):
        pass

    def test_forgot_password_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        response = apex.views.forgot_password(request)
        self.assertEqual(len(response['form'].errors), 1)

    def test_forgot_password(self):
        pass

    def test_reset_password_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        response = apex.views.reset_password(request)
        self.assertEqual(len(response['form'].errors), 2)

    def test_reset_password(self):
        pass

    def test_activate_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        response = apex.views.reset_password(request)
        self.assertEqual(len(response['form'].errors), 2)

    def test_activate(self):
        pass

    def test_register_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        response = apex.views.register(request)
        self.assertEqual(len(response['form'].errors), 4)

    def test_register(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        request.POST['login'] = 'test'
        request.POST['password'] = 'password'
        request.POST['password2'] = 'password'
        request.POST['email'] = 'mau@wau.de'
        response = apex.views.register(request)
        self.assertEqual(response.status, "302 Found")

    def test_add_auth_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        response = apex.views.add_auth(request)
        self.assertEqual(len(response['form'].errors), 4)

    def test_add_auth(self):
        pass

    def test_apex_callback_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        request.POST['token'] = 'test'
        response = apex.views.apex_callback(request)
        self.assertEqual(response.status, "302 Found")

    def test_apex_callback(self):
        pass

    def test_openid_required_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        self.assertRaises(AttributeError, apex.views.openid_required, request)

    def test_openid_required(self):
        pass

    def test_forbidden(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.matched_route = None
        response = apex.views.forbidden(request)
        # TODO return something != 200 OK
        self.assertEqual(response.status, "200 OK")

    def test_edit_fail(self):
        request = testing.DummyRequest(environ=environ)
        request.context = testing.DummyResource()
        request.method = 'POST'
        request.POST = webob.multidict.MultiDict()
        self.assertRaises(AttributeError, apex.views.edit, request)

    def test_edit(self):
        pass
