#!/usr/bin/env python
from zope.interface import implements, Interface

class IUserCreatedEvent(Interface):
    """Marker interface"""

class UserCreatedEvent(object):
    implements(IUserCreatedEvent)
    def __init__(self, request, user):
        self.request = request
        self.user = user

# vim:set et sts=4 ts=4 tw=0: 
