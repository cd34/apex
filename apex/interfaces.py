from zope.interface import implements
from zope.interface import Interface

class IApex(Interface):
    """ Class so that we can tell if Apex is installed from other 
    applications
    """
    pass

class ApexImplementation(object):
    """ Class so that we can tell if Apex is installed from other 
    applications
    """
    implements(IApex)
