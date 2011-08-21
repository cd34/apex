import unittest
from pyramid import testing

class TestView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_charset_defaults_to_utf8(self):
        r = self._makeOne({'PATH_INFO':'/'})
        self.assertEqual(r.charset, 'UTF-8')
