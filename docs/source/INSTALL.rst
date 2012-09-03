Installation Instructions
=========================

You'll need Velruse from Github to support many of the new features. If
you are using Velruse from pypi, do NOT use this branch.

You'll need to install Velruse from Github:

::

    easy_install -U https://github.com/bbangert/velruse/tarball/master

If you are converting from an older version of Apex, you'll need to
convert your database over to the new format.

::

    insert into auth_id (id) select id from auth_users;
    alter table auth_users add auth_id bigint unsigned after id;
    alter table auth_users add created datetime after email;
    alter table auth_users add provider varchar(80) default '' after auth_id;
    create unique index login_provider on auth_users (login,provider);
    update auth_users set auth_id=id;
    update auth_users set login=username,provider='local' where login='';
    alter table auth_users drop username;

    update auth_users set provider='google.com',login=replace(login,'$G$','') where login like '$G$%';
    update auth_users set provider='facebook.com',login=replace(login,'$F$','') where login like '$F$%';
    update auth_users set provider='twitter.com',login=replace(login,'$T$','') where login like '$T$%';


To use translations, you will need to use the following version of wtforms until it is pulled into the master

::

    easy_install -U https://bitbucket.org/kiorky/wtforms/get/77a9e3f0e0cd.tar.bz2

    https://bitbucket.org/kiorky/wtforms

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
    velruse.endpoint = http://domain.com/auth/apex_callback
    velruse.store = velruse.store.sqlstore
    velruse.store.url = mysql://username:password@localhost/database?use_unicode=0&charset=utf8
    velruse.openid.store = openid.store.memstore:MemoryStore
    velruse.openid.realm = http://domain.com/

    velruse.providers =
        velruse.providers.twitter

    velruse.twitter.consumer_key = 
    velruse.twitter.consumer_secret =

    [composite:main]
    use = egg:Paste#urlmap
    / = pexample
    /velruse = velruse

    [filter:exc]
    use=egg:WebError#evalerror

    [filter:tm]
    use=egg:repoze.tm2#tm

    [pipeline:pexample]
    pipeline = exc tm example

URLs to get your API keys:

Velruse Documentation: https://github.com/bbangert/velruse/blob/master/docs/providers.rst

* Facebook: https://developers.facebook.com/apps/
* Twitter: http://dev.twitter.com/apps/new
* Google: https://www.google.com/accounts/ManageDomains
* Yahoo: https://developer.apps.yahoo.com/projects
* Windows Live: http://msdn.microsoft.com/en-us/library/cc287659(v=MSDN.10).aspx

