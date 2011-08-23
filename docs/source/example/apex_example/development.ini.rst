development.ini
===============

::

    [app:apex_example]
    use = egg:apex_example
    reload_templates = true
    debug_authorization = false
    debug_notfound = false
    debug_routematch = false
    debug_templates = true
    default_locale_name = en
    sqlalchemy.url = sqlite:///%(here)s/apex_example.db

    mako.directories = apex_example:templates

    # at a minimum, the following 4 settings are required. If you have
    # already created a root factory, the secret's are not required.
    apex.session_secret = apex_example_session_secret
    apex.auth_secret = apex_example_auth_secret
    apex.came_from_route = home
    apex.velruse_config = %(here)s/CONFIG.yaml

    # we need to set up Velruse as an application
    [app:velruse]
    use = egg:velruse
    config_file = %(here)s/CONFIG.yaml
    beaker.session.data_dir = %(here)s/data/sdata
    beaker.session.lock_dir = %(here)s/data/slock
    beaker.session.key = velruse
    beaker.session.secret = somesecret
    beaker.session.type = cookie
    beaker.session.validate_key = STRONG_KEY_HERE
    # make sure you put the right domain here, otherwise, you'll get
    # a key error when trying to authenticate with an OpenID provider.
    beaker.session.cookie_domain = .domain.com

    [filter:exc]
    use=egg:WebError#evalerror

    # we use a pipeline to add the exception handler, tm, and our 
    # application
    [pipeline:papex_example]
    pipeline = exc tm apex_example

    # set up a composite app, mapping / to our application and /velruse
    # to velruse
    [composite:main]
    use = egg:Paste#urlmap
    / = papex_example
    /velruse = velruse

    [filter:tm]
    use = egg:repoze.tm2#tm
    commit_veto = repoze.tm:default_commit_veto

    [server:main]
    use = egg:Paste#http
    host = 0.0.0.0
    port = 8080

    # Begin logging configuration

    [loggers]
    keys = root, apex_example, sqlalchemy

    [handlers]
    keys = console

    [formatters]
    keys = generic

    [logger_root]
    level = INFO
    handlers = console

    [logger_apex_example]
    level = DEBUG
    handlers =
    qualname = apex_example

    [logger_sqlalchemy]
    level = INFO
    handlers =
    qualname = sqlalchemy.engine
    # "level = INFO" logs SQL queries.
    # "level = DEBUG" logs SQL queries and results.
    # "level = WARN" logs neither.  (Recommended for production systems.)

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = NOTSET
    formatter = generic

    [formatter_generic]
    format = %(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s

    # End logging configuration
