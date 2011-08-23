Deploying your application
==========================

**Apache**

::

    Alias /apex/static/ /path/to/virtualenv/lib/python2.6/site-packages/Apex-0.9.0-py2.6.egg/apex/static/

**Nginx**

::

    location ^~ /apex/static/ {
        alias   /path/to/virtualenv/lib/python2.6/site-packages/Apex-0.9.0-py2.6.egg/apex/static/;
    }
