class MessageException(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)

class ApexAuthSecret(MessageException):
    """ Exception called if there is no Auth Secret
    """
    message = 'Unable to find the apex.auth_secret setting, check your settings.'

class ApexSessionSecret(MessageException):
    """ Exception called if there is no Session Secret
    """
    message = 'Unable to find the apex.session_secret setting, check your settings.'
