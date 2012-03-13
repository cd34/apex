Deploying your application
==========================

**Apache**

::

    Alias /apex/static/ /path/to/virtualenv/lib/python2.7/site-packages/Apex-0.9.5-py2.7.egg/apex/static/

**Nginx**

::

    location ^~ /apex/static/ {
        alias   /path/to/virtualenv/lib/python2.7/site-packages/Apex-0.9.5-py2.7.egg/apex/static/;
    }
