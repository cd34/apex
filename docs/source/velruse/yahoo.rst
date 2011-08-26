Yahoo
=======

Go to:

https://developer.apps.yahoo.com/projects

Sign in.

Click **New Project**

Application Type: Standard

Application Name, Kind of Application (Web Based), Description Application 
URL and Favicon URL

Application Domain: http://domain.com/

Access Scopes: This app will only access public APIs, Web Services, or RSS feeds.

Agree to Terms of Use.

After you agree to the terms, you're presented with a page that contains your
Consumer Key and Consumer Secret.

Modify your **CONFIG.yaml** file to include the following:

::

    Yahoo:
        Consumer Key: (key from page under Authentication Information)
        Consumer Secret: (secret from page under Authentication Information)
