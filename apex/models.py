from cryptacular.bcrypt import BCRYPTPasswordManager
import transaction

from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid.util import DottedNameResolver

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy.sql.expression import func

from velruse.store.sqlstore import SQLBase

from zope.sqlalchemy import ZopeTransactionExtension 

from apex.lib.db import get_or_create
from apex.events import UserCreatedEvent

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

user_group_table = Table('auth_user_groups', Base.metadata,
    Column('user_id', types.Integer(), \
        ForeignKey('auth_users.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('group_id', types.Integer(), \
        ForeignKey('auth_groups.id', onupdate='CASCADE', ondelete='CASCADE'))
)

class AuthGroup(Base):
    """ Table name: auth_groups
    
::

    id = Column(types.Integer(), primary_key=True)
    name = Column(Unicode(80), unique=True, nullable=False)
    description = Column(Unicode(255), default=u'')
    """
    __tablename__ = 'auth_groups'
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(types.Integer(), primary_key=True)
    name = Column(Unicode(80), unique=True, nullable=False)
    description = Column(Unicode(255), default=u'')

    users = relationship('AuthUser', secondary=user_group_table, \
                     backref='auth_groups')

    def __repr__(self):
        return u'%s' % self.name

    def __unicode__(self):
        return self.name
    

class AuthUser(Base):
    """ Table name: auth_users

::

    id = Column(types.Integer(), primary_key=True)
    login = Column(Unicode(80), default=u'', index=True)
    username = Column(Unicode(80), default=u'', index=True)
    _password = Column('password', Unicode(80), default=u'')
    email = Column(Unicode(80), default=u'', index=True)
    active = Column(types.Enum(u'Y',u'N',u'D'), default=u'Y')
    """
    __tablename__ = 'auth_users'
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(types.Integer(), primary_key=True)
    login = Column(Unicode(80), default=u'', index=True)
    username = Column(Unicode(80), default=u'', index=True)
    _password = Column('password', Unicode(80), default=u'')
    email = Column(Unicode(80), default=u'', index=True)
    active = Column(types.Enum(u'Y',u'N',u'D', name=u"active"), default=u'Y')

    groups = relationship('AuthGroup', secondary=user_group_table, \
                      backref='auth_users')

    last_login = relationship('AuthUserLog', \
                         order_by='AuthUserLog.id.desc()')
    login_log = relationship('AuthUserLog', \
                         order_by='AuthUserLog.id')
    """
    Fix this to use association_proxy
    groups = association_proxy('user_group_table', 'authgroup')
    """

    def _set_password(self, password):
        self._password = BCRYPTPasswordManager().encode(password, rounds=12)

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password, \
                       _set_password))

    def in_group(self, group):
        """
        Returns True or False if the user is or isn't in the group.
        """
        return group in [g.name for g in self.groups]

    @classmethod
    def get_by_id(cls, id):
        """ 
        Returns AuthUser object or None by id

        .. code-block:: python

           from apex.models import AuthUser

           user = AuthUser.get_by_id(1)
        """
        return DBSession.query(cls).filter(cls.id==id).first()    

    @classmethod
    def get_by_login(cls, login):
        """ 
        Returns AuthUser object or None by login

        .. code-block:: python

           from apex.models import AuthUser

           user = AuthUser.get_by_login('$G$1023001')
        """
        return DBSession.query(cls).filter(cls.login==login).first()

    @classmethod
    def get_by_username(cls, username):
        """ 
        Returns AuthUser object or None by username

        .. code-block:: python

           from apex.models import AuthUser

           user = AuthUser.get_by_username('username')
        """
        return DBSession.query(cls).filter(cls.username==username).first()

    @classmethod
    def get_by_email(cls, email):
        """ 
        Returns AuthUser object or None by email

        .. code-block:: python

           from apex.models import AuthUser

           user = AuthUser.get_by_email('email@address.com')
        """
        return DBSession.query(cls).filter(cls.email==email).first()

    @classmethod
    def check_password(cls, **kwargs):
        if kwargs.has_key('id'):
            user = cls.get_by_id(kwargs['id'])
        if kwargs.has_key('username'):
            user = cls.get_by_username(kwargs['username'])

        if not user:
            return False
        if BCRYPTPasswordManager().check(user.password, kwargs['password']):
            return True
        else:
            return False

    def get_profile(self, request=None):
        """
        Returns AuthUser.profile object, creates record if it doesn't exist.

        .. code-block:: python

           from apex.models import AuthUser

           user = AuthUser.get_by_id(1)
           profile = user.get_profile(request)

        in **development.ini**

        .. code-block:: python

           apex.auth_profile = 
        """
        if not request:
            request = get_current_request()

        auth_profile = request.registry.settings.get('apex.auth_profile')
        if auth_profile:
            resolver = DottedNameResolver(auth_profile.split('.')[0])
            profile_cls = resolver.resolve(auth_profile)
            return get_or_create(DBSession, profile_cls, user_id=self.id)

class AuthUserLog(Base):
    """
    event: 
      L - Login
      R - Register
      P - Password
      F - Forgot
    """
    __tablename__ = 'auth_user_log'
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(types.Integer, primary_key=True)
    user_id = Column(types.Integer, ForeignKey(AuthUser.id), index=True)
    time = Column(types.DateTime(), default=func.now())
    ip_addr = Column(Unicode(39), nullable=False)
    event = Column(types.Enum(u'L',u'R',u'P',u'F', name=u"event"), default=u'L')

def populate(settings):
    session = DBSession()
    
    default_groups = []
    if settings.has_key('apex.default_groups'):
        for name in settings['apex.default_groups'].split(','):
            default_groups.append((unicode(name.strip()),u''))
    else:
        default_groups = [(u'users',u'User Group'), \
                          (u'admin',u'Admin Group')]
    for name, description in default_groups:
        group = AuthGroup(name=name, description=description)
        session.add(group)

    session.flush()
    transaction.commit()

def initialize_sql(engine, settings):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    if settings.has_key('apex.velruse_config'):
        SQLBase.metadata.bind = engine
        SQLBase.metadata.create_all(engine)
    try:
        populate(settings)
    except IntegrityError:
        transaction.abort()

def create_user(**kwargs):
    """
::

    from apex.lib.libapex import create_user
    create_user(username='test', password='my_password', active='Y', group='group')
    Returns: AuthUser object
    """
    user = AuthUser()
    request = get_current_request()
    registry = get_current_registry()
    settings = registry.settings
    if settings.has_key('apex.default_user_group'):
        group = DBSession.query(AuthGroup). \
           filter(AuthGroup.name==settings['apex.default_user_group']).one()
        user.groups.append(group)
    DBSession.flush()
    if 'group' in kwargs:
        try:
            group = DBSession.query(AuthGroup). \
            filter(AuthGroup.name==kwargs['group']).one()
            user.groups.append(group)
        except NoResultFound:
            pass
        del kwargs['group']
    for key, value in kwargs.items():
        setattr(user, key, value)
    DBSession.add(user)
    DBSession.flush()
    registry.notify(UserCreatedEvent(request, user))
    return user


