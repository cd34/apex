import unittest
from pyramid import testing

class Test_lib_libapex(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    #    request = testing.DummyRequest()
    #    request.context = testing.DummyResource()

    def test_apexid_from_url_google(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$G$xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', apexid_from_url('Google','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))

    def test_apexid_from_url_twitter(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$T$xxxxxxxx', apexid_from_url('Twitter',"http://twitter.com/?id=['xxxxxxxx']"))

    def test_apexid_from_url_facebook(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$F$xxxxxxxxxx', apexid_from_url('Facebook','https://graph.facebook.com/xxxxxxxxxx'))
