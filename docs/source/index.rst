.. Apex documentation master file, created by
   sphinx-quickstart on Sat Aug 20 15:40:57 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Apex's documentation!
================================

**Quick Overview**

Apex is a framework that works on top of Pyramid_ focused on simplifying
authentication, but, also activating a number of other features. Apex
has a single user model and encourages you to use a Foreign Key relation
to any Profile information you would like to store.

**What is included?**

Authentication, Form Library, I18N/L10N, Flash Message Template

Uses pyramid_routesalchemy

**Authentication**

  * Local authentication uses BCrypt
  * http://codahale.com/how-to-safely-store-a-password/

Velruse_ is used for OpenID/OpenAuth providers and supports:
  * Google
  * Facebook
  * github
  * Twitter
  * Yahoo
  * Microsoft Live
  * Any OpenID provider

Ability to overload the login form, extend the AuthUser class through
polymorphism or a Foreign Key user profile table.

**Form Library**

WTForms_ is used to help those transitioning over from Django to Pyramid.

**I18N/L10N**

Babel_ is used to support Internationalization and Localization.

**Flash Messages**

Templates and helpers for Mako_ and Jinja2_ are included to support Flash
Messages in your application.

Contents:

.. toctree::
   :maxdepth: 2

   INSTALL
   QUICKSTART
   routes
   deployment
   options
   extending_profile
   redefine_login_page
   lib/index
   models
   decorators
   exceptions
   forms
   interfaces
   views
   extensions
   templates
   velruse/index
   example/index
   wishlist

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _WTForms: http://wtforms.simplecodes.com/
.. _Babel: http://babel.edgewall.org/
.. _Pyramid: http://www.pylonsproject.org/
.. _Velruse: https://github.com/bbangert/velruse
.. _Mako: http://www.makotemplates.org/
.. _Jinja2: http://jinja.pocoo.org/
