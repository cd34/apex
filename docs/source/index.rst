.. Apex documentation master file, created by
   sphinx-quickstart on Sat Aug 20 15:40:57 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Apex's documentation!
================================

Authentication, Form Library, I18N/L10N, Flash Message Template
(not associated with Pyramid, a Pylons project)

Uses pyramid_routesalchemy

Authentication

  * Local authentication uses BCrypt
  * http://codahale.com/how-to-safely-store-a-password/

Velruse is used for OpenID/OpenAuth providers and supports
  * Google
  * Facebook
  * Twitter
  * Yahoo
  * Microsoft Live
  * Any OpenID provider

Ability to overload the login form, extend the AuthUser class through
polymorphism or a Foreign Key user profile table.

* Form Library

WTForms is used to help those transitioning over from Django to Pyramid.

* I18N/L10N

Babel is used to support Internationalization and Localization.

* Flash Messages

Templates and helpers for Mako and Jinja2 are included to support Flash
Messages in your application.

Contents:

.. toctree::
   :maxdepth: 2

   INSTALL
   QUICKSTART
   models
   extending_profile
   extensions
   models
   options
   redefine_login_page
   subscribers
   templates
   ext/deform
   velruse/google
   velruse/facebook
   velruse/twitter

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

