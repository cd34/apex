Authentication, Form Library, I18N/L10N, Flash Message Template
(not associated with Pyramid, a Pylons project)

Uses alchemy

* Authentication

Authentication has a single authentication id which can have multiple
associated credentials. A user can create a username and associate their
Facebook and Google login records with their current record and log in
with any of them. It is planned that Apex will act as an endpoint for
multi-domain multi-site installations - allowing one to associate a login
account from one domain to another.

Local authentication uses salt + BCrypt
http://codahale.com/how-to-safely-store-a-password/

Velruse is used for OpenID/OpenAuth providers and supports
  * Google
  * Facebook
  * Twitter
  * Yahoo
  * Microsoft Live
  * Bitbucket
  * Github
  * Identi.ca
  * Last.fm
  * LinkedIn
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
