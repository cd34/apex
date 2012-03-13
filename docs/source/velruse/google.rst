Google
======

Go to:

https://www.google.com/accounts/ManageDomains

Sign in.

Add a new Domain:

domain.com

Manage the domain - you'll need to handle their verification process. After
you've verified the domain, you'll need to activate it. For the Target
URL path prefix put:

http://domain.com/velruse/logged_in

Once you've done this, you're presented with your OAuth Consumer Key
and OAuth Consumer Secret.

Modify your **development.ini** file to include the following:

::

    # OpenID storage required by:
    # google, yahoo and openid providers
    velruse.openid.store = openid.store.memstore:MemoryStore
    velruse.openid.realm = http://domain.com

    # Google (also requires OpenID configuration)
    velruse.google.consumer_key =
    velruse.google.consumer_secret =
    velruse.google.oauth_scope =
