"""
from nose.tools import eq_
from nose.tools import raises

from apex.lib.libapex import apexid_from_url

from velruse.baseconvert import base_encode, base_decode

class TestBaseEncoding(object):
    def test_encode(self):
        eq_(base_encode(42), 'L')
        eq_(base_encode(425242), '4rBC')
        eq_(base_encode(0), '2')

class test_apexid_from_url(object):
    def test_valid(self):
        eq_(apexid_from_url('Google','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'), '$G$xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        eq_(apexid_from_url('Twitter',"http://twitter.com/?id=['xxxxxxxx']"), '$T$xxxxxxxx')
        eq_('$F$xxxxxxxxxx', apexid_from_url('Facebook','https://graph.facebook.com/xxxxxxxxxx'))
        eq_('$Y$xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx', apexid_from_url('Yahoo','https://me.yahoo.com/a/xxxxxxxxxxxxxxxxxx.xxxxx#xxxxx'))

    @raises(ValueError)
    def test_invalid_provider(self):
        eq_(None, apexid_from_url('Blah','https://www.google.com/accounts/o8/id?id=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))

    @raises(ValueError)
    def test_invalid_url(self):
        eq_(None, apexid_from_url('Google','https://www.google.com/accounts/o8/id?xx=xxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
        eq_(None, apexid_from_url('Twitter',"http://twitter.com/?xx=['xxxxxxxx']"))
        eq_(None, apexid_from_url('Facebook','https://graph.facebook.com'))
        eq_(None, apexid_from_url('Yahoo','https://me.yahoo.com/a'))

"""
