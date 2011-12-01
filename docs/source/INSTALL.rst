Installation Instructions
=========================

Temporarily, 1.2a1 as installed from easy_install pyramid has a bug with
the Root Factory. You'll need to install Pyramid from Github:

::

    easy_install -U https://github.com/Pylons/pyramid/tarball/master

**__init__.py**

::

    # place this line in __init__.py above
    # return config.make_wsgi_app()

    config.include('apex', route_prefix='/auth')

**development.ini**

::

    # if you need to confirm by mail on account creation
    apex.need_mail_verification = true
    apex.session_secret = asdfasdf
    apex.auth_secret = abcdefgh
    apex.came_from_route = index
    apex.velruse_config = %(here)s/CONFIG.yaml
    apex.recaptcha_public_key = asdfasdf
    apex.recaptcha_private_key = asdfasdf
    apex.use_recaptcha_on_login = false
    apex.use_recaptcha_on_forgot = false
    apex.use_recaptcha_on_reset = false
    apex.use_recaptcha_on_register = true
    apex.provider_exclude = openid
    # comma separated list of providers to exclude even if OpenID settings are
    # set in the config file
    apex.register_form_class = package.forms.MyRegisterForm

    # Apex looks at the Auth Providers configured by Velruse to build the login
    # page

    [app:velruse]
    use = egg:velruse
    velruse.providers=
        velruse.providers.github

    [composite:main]
    use = egg:Paste#urlmap
    / = pexample
    /velruse = velruse

    [filter:exc]
    use=egg:WebError#evalerror

    [pipeline:pexample]
    pipeline = exc tm example

URLs to get your API keys:

Velruse Documentation: https://github.com/bbangert/velruse/blob/master/docs/providers.rst

* Facebook: https://developers.facebook.com/apps/
* Twitter: http://dev.twitter.com/apps/new
* Google: https://www.google.com/accounts/ManageDomains
* Yahoo: https://developer.apps.yahoo.com/projects
* Windows Live: http://msdn.microsoft.com/en-us/library/cc287659(v=MSDN.10).aspx

