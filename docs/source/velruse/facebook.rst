Facebook
========

Go to:

https://developers.facebook.com/apps/

Sign in.

Create New App (Upper Right Corner)

Put in an Application Name and agree to the terms.

Solve the Recaptcha.

Left hand side, Click Web.

For Site URL, put the URL of your site.

Site Domain should be the domain of your site, and needs to be part of the
site URL. So, if you use http://specialname.domain.com, you would need to 
put domain.com or specialname.domain.com. You cannot specify a separate domain.

Modify your **development.ini** file to include the following:

::

    provider.facebook.consumer_key =
    provider.facebook.consumer_secret =
    provider.facebook.scope = (optional)
