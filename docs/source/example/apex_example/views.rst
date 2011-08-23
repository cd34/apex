views
==========

::

    from pyramid.view import view_config

    @view_config(route_name='home', renderer='index.mako')
    def index(request):
        return {}

    @view_config(route_name='test', renderer='test.mako')
    def test(request):
        return {}

    @view_config(route_name='protected', renderer='protected.mako',
                 permission='authenticated')
    def protected(request):
        return {}

    @view_config(route_name='groupusers', renderer='groupusers.mako',
                 permission='users')
    def groupusers(request):
        return {}
