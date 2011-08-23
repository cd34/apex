import unittest

from pyramid import testing

class Test_lib_libapex(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_apexid_from_url(self):
        from apex.lib.libapex import apexid_from_url

        # Test Google
        self.assertEqual('$G$xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', apexid_from_url('Google','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
        self.assertEqual(None, apexid_from_url('Google','https://www.google.com/accounts/o8/id?xx=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))

        # Test Twitter
        self.assertEqual('$T$xxxxxxxx', apexid_from_url('Twitter',"http://twitter.com/?id=['xxxxxxxx']"))
        self.assertEqual(None, apexid_from_url('Twitter',"http://twitter.com/?xx=['xxxxxxxx']"))

        # Test Facebook
        self.assertEqual('$F$xxxxxxxxxx', apexid_from_url('Facebook','https://graph.facebook.com/xxxxxxxxxx'))
        self.assertEqual(None, apexid_from_url('Facebook','https://graph.facebook.com'))

        # Test Yahoo
        self.assertEqual('$Y$xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx', apexid_from_url('Yahoo','https://me.yahoo.com/a/xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx'))
        self.assertEqual(None, apexid_from_url('Yahoo','https://me.yahoo.com/a'))

        # Test Invalid Provider name
        self.assertEqual(None, apexid_from_url('Blah','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
