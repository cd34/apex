#!/usr/bin/env python
from zope.interface import implements, Interface

class IUserCreatedEvent(Interface):
    """Marker interface"""

class UserCreatedEvent(object):
    implements(IUserCreatedEvent)
    def __init__(self, request, user):
        self.request = request
        self.user = user

class IGroupCreatedEvent(Interface):
    """Marker interface"""

class GroupCreatedEvent(object):
    implements(IGroupCreatedEvent)
    def __init__(self, request, group):
        self.request = request
        self.group = group 


# vim:set et sts=4 ts=4 tw=0: 
