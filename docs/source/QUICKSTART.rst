Quickstart
==========

Temporarily, 1.2a1 as installed from easy_install pyramid has a bug with
the Root Factory. You'll need to install Pyramid from Github:

::

    easy_install -U https://github.com/Pylons/pyramid/tarball/master

To use translations, you'll need to use the following version of wtforms
until it is pulled into the master

    easy_install -U https://bitbucket.org/kiorky/wtforms/get/77a9e3f0e0cd.tar.bz2

    https://bitbucket.org/kiorky/wtforms

Initial Setup of Pyramid-Apex

::

  virtualenv --no-site-packages newenv
  cd newenv
  source bin/activate
  easy_install https://github.com/cd34/apex/tarball/master
  paster create -t pyramid_routesalchemy example
  cd example
  vi development.ini

**development.ini**

In the [app:example] section, add:

::

    apex.session_secret = CHANGEME
    # if you need to confirm by mail on account creation
    apex.need_mail_verification = true
    apex.auth_secret = CHANGEME
    apex.came_from_route = home
    # velruse host accessible both by the host and the clients.
    apex.velruse_url = http://localhost:port
    apex.recaptcha_public_key = xxxxxxxxxxxxxxxxxx
    apex.recaptcha_private_key = xxxxxxxxxxxxxxxxxx

    sqlalchemy.url = mysql://username:password@localhost/database?use_unicode=1&charset=utf8
    sqlalchemy.echo = false
    sqlalchemy.echo_pool = false
    sqlalchemy.pool_recycle = 10

If you do not include the recaptcha public and private key, the 
login/registration forms will not include the ReCaptcha.net form.

If you need to get a key for ReCaptcha.net, go to:
https://www.google.com/recaptcha/admin/create and 'Create Key'

For Velruse, we need to add the following:

::

    [app:velruse]
    use = egg:velruse
    velruse.providers=
        velruse.providers.someprovider
    velruse.providers.someprovider.consumer_key = xxxx
    velruse.providers.someprovider.consumer_secret = xxxx

Comment or remove the following settings:

::

    [pipeline:main]
    pipeline =
        egg:WebError#evalerror
        tm
        example

Add the following settings:

::

    [filter:exc]
    use=egg:WebError#evalerror

    [pipeline:pexample]
    pipeline = exc tm example

    [composite:main]
    use = egg:Paste#urlmap
    / = pexample
    /velruse = velruse

If you are going to be developing with this virtualenv:

::

    python setup.py develop

Create your CONFIG.yaml file for Velruse. Currently, we need to access the
backing store, so, we've opted to use Type: SQL. You can use any store as
long as the backend can be read without calling /velruse/authinfo. The
Memory Store requires the additional urllib2 call.


In **example/__init__.py**, before the return config.make_wsgi_app(), put:

::

    # place this line in __init__.py above
    # return config.make_wsgi_app()

    config.include('apex', route_prefix='/auth')

In **example/__init__.py**, we'll add the following route:

::

    config.add_route('protected', '/protected')
    config.add_view('example.views.my_view',
                    route_name='protected',
                    renderer='templates/mytemplate.pt',
                    permission='authenticated')

The default permissions are view and authenticated. Additionally, groups
of user and admin are created.

If you want to use a group, the group name is used for the permission setting
on the view.

::

    config.add_route('groupusers', '/groupusers')
    config.add_view('example.views.my_view',
                    route_name='groupusers',
                    renderer='templates/mytemplate.pt',
                    permission='users')
