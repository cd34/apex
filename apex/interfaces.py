from zope.interface import implements
from zope.interface import Interface

class IApex(Interface):
    pass
    
class ApexImplementation(object):
    implements(IApex)
