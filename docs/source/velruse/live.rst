Microsoft Live
==============

Go to:

http://msdn.microsoft.com/en-us/library/cc287659(v=MSDN.10).aspx

Under the section: **To get your client ID**

Go to the Windows Live application management site.

Sign in.

Application Name: (your application name)
Language: English

Modify your **CONFIG.yaml** file to include the following:

::

    Live:
        Application ID: (Client ID)
        Secret Key: (Client secret)
        Policy URL: http://domain.com/policy.html
        Offers: Contacts.View

If you are using Live, and are not using Velruse 0.20a1dev, you need to do:

::

    easy_install -U https://github.com/bbangert/velruse/tarball/master
