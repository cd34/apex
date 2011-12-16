Extending Profile
=================

If you are using a local authentication database:

**models/__init__.py**

::

    from apex.models import AuthID

    class ForeignKeyProfile(Base):
        __tablename__ = 'auth_user_profile'

        id = Column(types.BigInteger, primary_key=True)
        user_id = Column(types.BigInteger, ForeignKey(AuthID.id), index=True)

        """ Add your locally defined options here
        """
        first_name = Column(Unicode(80))
        last_name = Column(Unicode(80))

        user = relationship(AuthID, backref=backref('profile', uselist=False))

**project/models/profile.py**

::

    from apex.forms import RegisterForm

    from project.models import DBSession
    from project.models import ForeignKeyProfile

    class NewRegisterForm(RegisterForm):
    def after_signup(self, user):
            profile = ForeignKeyProfile(user_id=user.id)
            DBSession.add(profile)
            DBSession.flush()

**development.ini**

::

    apex.register_form_class = project.form.NewRegisterForm


If you are using OpenID providers:

**development.ini**

::

    apex.create_openid_after = project.form.openid_after

**project/models/__init__.py**

::

    class ForeignKeyProfile(Base):
        __tablename__ = 'auth_user_profile'

        id = Column(types.BigInteger, primary_key=True)
        user_id = Column(types.BigInteger, ForeignKey(AuthUser.id))

        """ Add your locally defined options here
        """
        first_name = Column(Unicode(80))
        last_name = Column(Unicode(80))

        user = relationship('AuthUser', backref=backref('profile', uselist=False))

**project/models/profile.py**

::

    from apex.forms import RegisterForm

**project/profile.py**

::

    from project.models import DBSession
    from project.models import ForeignKeyProfile

    class openid_after(object):
        def after_signup(self, user):
            profile = ForeignKeyProfile(user_id=user.id)
            DBSession.add(profile)
            DBSession.flush()

    AuthUser.get_profile()
