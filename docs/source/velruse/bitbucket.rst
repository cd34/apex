Bitbucket
=========

::

    INCOMPLETE

Go to:

http://

Sign in.

Application Name, Description and Website are not critical, but, are required
fields. Set the Callback URL to:

http://yourdomain.com/velruse/logged_in

After you agree to the terms, you're presented with a page that contains your
Consumer Key and Consumer Secret.

Click the button, Create my Access token

Modify your **development.ini** file to include the following:

::

    velruse.bitbucket.consumer_key =
    velruse.bitbucket.consumer_secret =
    velruse.bitbucket.authorize = true
