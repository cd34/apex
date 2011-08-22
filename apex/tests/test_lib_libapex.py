import unittest

from pyramid import testing

class Test_lib_libapex(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_apexid_from_url_google(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$G$xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', apexid_from_url('Google','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
        self.assertEqual(None, apexid_from_url('Google','https://www.google.com/accounts/o8/id?xx=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))

    def test_apexid_from_url_twitter(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$T$xxxxxxxx', apexid_from_url('Twitter',"http://twitter.com/?id=['xxxxxxxx']"))
        self.assertEqual(None, apexid_from_url('Twitter',"http://twitter.com/?xx=['xxxxxxxx']"))

    def test_apexid_from_url_facebook(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$F$xxxxxxxxxx', apexid_from_url('Facebook','https://graph.facebook.com/xxxxxxxxxx'))
        self.assertEqual(None, apexid_from_url('Facebook','https://graph.facebook.com'))

    def test_apexid_from_url_yahoo(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual('$Y$xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx', apexid_from_url('Yahoo','https://me.yahoo.com/a/xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx'))
        self.assertEqual(None, apexid_from_url('Yahoo','https://me.yahoo.com/a'))

    def test_apexid_from_url_invalid_provider(self):
        from apex.lib.libapex import apexid_from_url

        self.assertEqual(None, apexid_from_url('Blah','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
