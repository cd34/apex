from zope.interface import implementer
from zope.interface import Interface

class IApex(Interface):
    """ Class so that we can tell if Apex is installed from other 
    applications
    """
    pass

@implementer(IApex)
class ApexImplementation(object):
    """ Class so that we can tell if Apex is installed from other 
    applications
    """
    pass
