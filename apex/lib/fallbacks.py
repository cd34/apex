import hashlib

from apex.lib.libapex import apex_settings

"""
This fallback routine attempts to check existing hashes that have failed
the bcrypt check against md5, hardcoded salt+md5, fieldbased salt+md5,
sha1, hardcoded salt+sha1, fieldbased salt+md5, and plaintext.

If any of the hash methods match, the user record is updated with the new
password. You can also write your own GenericFallback class to handle 
any other authentication scheme.

Options set in (development|production).ini:

apex.fallback_prefix_salt = salt to be prepended to password string
apex.fallback_salt_field = field in user table containing salt

"""

class GenericFallback(object):
    def check(self, DBSession, request, user, password):
        salted_passwd = user.password
        prefix_salt = apex_settings('fallback_prefix_salt', None)
        if prefix_salt:
            salted_passwd = '%s%s' % (prefix_salt, salted_passwd)
        salt_field = apex_settings('fallback_salt_field', None)
        if salt_field:
            prefix_salt = getattr(user, salt_field)
            salted_passwd = '%s%s' % (prefix_salt, salted_passwd)

        if salted_passwd is not None:
            if len(salted_passwd) == 32:
                # md5
                m = hashlib.md5()
                # password='····� breaks when type=unicode
                m.update(password)
                if m.hexdigest() == salted_passwd:
                    user.password = password
                    DBSession.merge(user)
                    DBSession.flush()
                    return True

            if len(salted_passwd) == 40:
                # sha1
                m = hashlib.sha1()
                m.update(password)
                if m.hexdigest() == salted_passwd:
                    user.password = password
                    DBSession.merge(user)
                    DBSession.flush()
                    return True

            if salted_passwd == password:
                # plaintext
                user.password = password
                DBSession.merge(user)
                DBSession.flush()
                return True

        return False
