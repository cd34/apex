from zope.interface import implements
from zope.interface import Interface

class IPyramidApex(Interface):
    pass
    
class PyramidApexImplementation(object):
    implements(IPyramidApex)