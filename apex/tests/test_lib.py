import unittest
from pyramid import testing

class MyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    #    request = testing.DummyRequest()
    #    request.context = testing.DummyResource()

    def test_googleid(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$G$12345', apexid_from_url('Google','http://blah.com/?id=12345'))
