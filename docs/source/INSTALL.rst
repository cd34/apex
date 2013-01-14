Installation Instructions
=========================

**__init__.py**

::

    # place this line in __init__.py above
    # return config.make_wsgi_app()

    config.include('apex', route_prefix='/auth')

**development.ini**

::

    apex.session_secret = asdfasdf
    apex.auth_secret = abcdefgh
    apex.came_from_route = index
    apex.recaptcha_public_key = asdfasdf
    apex.recaptcha_private_key = asdfasdf
    apex.use_recaptcha_on_login = false
    apex.use_recaptcha_on_forgot = false
    apex.use_recaptcha_on_reset = false
    apex.use_recaptcha_on_register = true
    apex.no_csrf = login,apex_callback
    # comma separated list of providers to use
    apex.velruse_providers = twitter
    apex.register_form_class = package.forms.MyRegisterForm

    [app:velruse]
    use = egg:velruse
    debug = false
    endpoint = http://domain.com/auth/apex_callback
    openid.store = openid.store.memstore:MemoryStore
    openid.realm = http://domain.com/

    providers =
        providers.twitter

    providers.twitter.consumer_key = 
    providers.twitter.consumer_secret =

    [composite:main]
    use = egg:Paste#urlmap
    / = pexample
    /velruse = velruse

    [filter:exc]
    use=egg:WebError#evalerror

    [pipeline:pexample]
    pipeline = exc example

URLs to get your API keys:

Velruse Documentation: https://github.com/bbangert/velruse/blob/master/docs/providers.rst

* Facebook: https://developers.facebook.com/apps/
* Twitter: http://dev.twitter.com/apps/new
* Google: https://www.google.com/accounts/ManageDomains
* Yahoo: https://developer.apps.yahoo.com/projects
* Windows Live: http://msdn.microsoft.com/en-us/library/cc287659(v=MSDN.10).aspx

