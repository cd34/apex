Options
=======

**development.ini** settings

apex.session_secret = sess_secret
  **REQUIRED**, defines the session secret used for Pyramid

apex.auth_secret = auth_secret
  **REQUIRED**, defines the authentication secret used for Pyramid

apex.came_from_route = home
  **REQUIRED**, defines the default home route. Pyramid defaults to home, but
  some installations may use index, etc.

apex.recaptcha_public_key = 
  OPTIONAL, REQUIRED if using Recaptcha

apex.recaptcha_private_key = 
  OPTIONAL, REQUIRED if using Recaptcha

apex.use_recaptcha_on_login = false
  OPTIONAL, Display Recaptcha form on Login Page

apex.use_recaptcha_on_forgot = false
  OPTIONAL, Display Recaptcha form on Forgot my Password Page

apex.use_recaptcha_on_reset = false
  OPTIONAL, Display Recaptcha form on Reset my Password Page

apex.use_recaptcha_on_register = true
  OPTIONAL, Display Recaptcha form on Registration Page

apex.exclude_local = false
  OPTIONAL, disable local authentication

apex.velruse_providers = 
  OPTIONAL, comma separated list to include velruse configured providers.

apex.apex_template = project:templates/auth.mako
  OPTIONAL, an optional template for rendering the authentication forms

apex.form_template = project:templates/form.mako
  OPTIONAL, an optional template for changing the default template used when
  rendering forms

apex.register_form_class = project.models.form_name
  OPTIONAL, requires DOTTED notation, specifies overloaded form for
  registration

apex.default_user_group = 
  OPTIONAL, If defined, will add the user to this group when created. If
  undefined, users will not be assigned to a group and you'll only have the
  permissions 'view' and 'authenticated'.

apex.create_openid_before =
  OPTIONAL, NOT IMPLEMENTED, since OpenID requests don't allow us to
  override the signup form, we call this function before the OpenID
  Provider call.

apex.create_openid_after =
  OPTIONAL, since OpenID requests don't allow us to override the signup
  form, we call this function after the OpenID callback.

apex.openid_required =
  OPTIONAL, comma separated list of required fields when using OpenID to create
  an account

apex.default_groups = 
  OPTIONAL, comma separated list of group names to create. Defaults to 
  admin,user

apex.log_logins = false
  OPTIONAL, boolean flag to log timestamp and IP address on each login.
 
apex.log_login_header =
  OPTIONAL, Default value is to use REMOTE_ADDR, but, if you run behind
  a cache or proxy server, you might need to set this to X-Forwarded-For
  or another header value that contains the Real IP address of the surfer.

apex.use_apex_edit = false
  OPTIONAL, use apex's model form profile edit function. This is a quick,
  simple function.

apex.no_csrf = 
  OPTIONAL, a comma separated list of route names that should NOT be subject
  to CSRF tests.

**Email Settings**

Email Messages that Apex sends can be customized. The following replacements
are made on messages:

* %_url_% - URL of the Reset Password form

apex.sender_email = 
  OPTIONAL, defaults to nobody@example.com

apex.email_validate = false
  OPTIONAL, require email address to be validated before activating account.

apex.email_message_text = apex.lib.libapex.EmailMessageText
  OPTIONAL, dotted class notation containing replacement message text

apex.use_request_factory = true
  OPTIONAL, use apex's default request factory

**Fallback Authorization**

Fallback Authorization is optional and is used for transitioning a 
local user authentication table over to a native Apex salt+BCrypt. If
you are running an existing authentication system, this eliminates
having to reset everyone's password and send notifications for an existing
auth system as you can run both in parallel and Apex will convert the
user to native salt+BCrypt after a successful login. By default, Apex 
includes a generic fallback that guesses between md5, sha1 and plaintext.

apex.fallback_auth = 
  OPTIONAL, use apex.lib.fallbacks.GenericFallback which will handle md5,
  prefix salt+md5, table field salt+md5, sha1, prefix salt+sha1, table field
  salt+sha1 and plaintext. If a local password fails bcrypt, you can enable
  the fallback to check other schemes and update the password table.
  You can also write your own callback to match your existing password
  hash method.

apex.fallback_prefix_salt = 
  OPTIONAL, salt to be prepended to password string

apex.fallback_salt_field = 
  OPTIONAL, field in user table containing salt

apex.max_cookie_age = None
  OPTIONAL, set the max cookie age in seconds

**Future**

apex.max_local_logins = 1
  OPTIONAL, controls the number of local authentication records that can
  be assigned to a single user.
