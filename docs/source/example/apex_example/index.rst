Apex Example
================================

To get started, create a virtualenv for your test, activate it and copy 
the example code:

::

    virtualenv /var/www/apex_example
    cd /var/www/apex_example
    source bin/activate
    easy_install -U pyramid
    easy_install -U distribute
    git clone git@github.com:cd34/apex.git
    cd apex/examples/apex_example
    python setup.py develop

Due to a bug in the version of distribute that ships with virtualenv and
one of apex's dependencies, you need to do:

::

    easy_install -U distribute

This example is a very minimal project that will allow you to register, 
login, log out, change your password, etc. By default, you cannot go
to the groupusers url as users are not added to any group. You can 
override this by adding:

::

    apex.default_user_group = users

Contents:

.. toctree::
   :maxdepth: 2

   development.ini
   init
   models
   views


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

