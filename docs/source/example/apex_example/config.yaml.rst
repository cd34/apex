CONFIG.yaml
===========

This is the minimal configuration required to get Velruse working for OpenID.
You can add other directives to add other OpenID Providers.

::

    Store:
        Type: SQL
        DB: sqlite:///%(here)s/apex_example.db

    OpenID Store:
        Type: openid.store.memstore:MemoryStore
