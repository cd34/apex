Twitter
=======

Go to:

http://dev.twitter.com/apps/new

Sign in.

Application Name, Description and Website are not critical, but, are required
fields. Set the Callback URL to:

http://yourdomain.com/velruse/logged_in

After you agree to the terms, you're presented with a page that contains your
Consumer Key and Consumer Secret.

Click the button, Create my Access token

Modify your **development.ini** file to include the following:

::

    provider.twitter.consumer_key =
    provider.twitter.consumer_secret =
    provider.twitter.authorize = (optional)
