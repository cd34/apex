Wishlist/Future Features
========================

* Allow user to use multiple login credentials, i.e. Create an account and
  associate that account with both Google and Facebook, allowing them to
  log in with either Auth provider.

* Easier access to scope/permission models with sx,ax parameters.

* Configurable number of rounds for BCrypt - currently a load order
  instantiation issue.

* System currently uses HMAC to set token for password resets. Since 
  Velruse includes pycrypto, we have the ability to do public key
  encryption for added security.

* Remember me - customizable expiration checkbox. Currently sessions are
  available based on your default beaker expiration time. Auth should
  optionally allow a default of x seconds, and a checkbox that allows for 
  a longer signin session.
