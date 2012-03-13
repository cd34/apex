from pyramid.threadlocal import get_current_request

class Flash(object):
    """ There are 4 default queues, warning, notice, error and success
    """

    queues = ['warning', ''error', 'success', 'notice']
    default_queue = 'notice'
        
    def __init__(self, queues=None, default_queue=None, allow_duplicate=True):
        self.allow_duplicate = allow_duplicate

        if queues is not None:
            self.queues = queues
        if default_queue is not None:
            self.default_queue = default_queue

    def __call__(self, msg, queue=default_queue):
        request = get_current_request()
        request.session.flash(msg, queue, self.allow_duplicate)

    def get_all(self):
        """ Returns all queued Flash Messages
        """
        request = get_current_request()
        messages = []
        for queue in self.queues:
            for peeked in request.session.peek_flash(queue):
                messages.append({'message': peeked, 'queue': queue,})
            request.session.pop_flash(queue)
        return messages

flash = Flash(allow_duplicate=False)
