"""
initial test issue due to fact that we're not testing an app, but an include
"""
import unittest
from pyramid import testing

class Test_lib_libapex(unittest.TestCase):
    def setUp(self):
        #import apex
        self.config = testing.setUp()
        #self.config.include('apex')

    def tearDown(self):
        testing.tearDown()

    def test_logout(self):
        pass
        """
        from apex.views import logout
        request = testing.DummyRequest()
        request.context = testing.DummyResource()
        response = logout(request)

        self.assertEqual(response.status, 200)
        """

