import bcrypt
import transaction

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy import types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy.sql import functions

from velruse.store.sqlstore import SQLBase

from zope.sqlalchemy import ZopeTransactionExtension 

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

user_group_table = Table('auth_user_groups', Base.metadata,
    Column('user_id', types.BigInteger(), \
        ForeignKey('auth_users.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('group_id', types.BigInteger(), \
        ForeignKey('auth_groups.id', onupdate='CASCADE', ondelete='CASCADE'))
)

class AuthGroup(Base):
    __tablename__ = 'auth_groups'
    __table_args__ = {"sqlite_autoincrement": True}
    
    id = Column(types.BigInteger(), primary_key=True)
    name = Column(Unicode(80), unique=True, nullable=False)
    created = Column(types.DateTime(), default=functions.current_date())

    users = relation('AuthUser', secondary=user_group_table, \
                     backref='auth_groups')

    def __repr__(self):
        return u'%s' % self.name

    def __unicode__(self):
        return self.name
    

class AuthUser(Base):
    __tablename__ = 'auth_users'
    __table_args__ = {"sqlite_autoincrement": True}

    id = Column(types.BigInteger(), primary_key=True)
    login = Column(Unicode(80), default=u'', index=True)
    username = Column(Unicode(80), default=u'', index=True)
    _password = Column('password', Unicode(80), default=u'', index=True)
    email = Column(Unicode(80), default=u'', index=True)

    groups = relation('AuthGroup', secondary=user_group_table, \
                      backref='auth_users')

    def _set_password(self, password):
        self._password = bcrypt.hashpw(password, bcrypt.gensalt())

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password, \
                       _set_password))
    
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()    

    @classmethod
    def get_by_login(cls, login):
        return DBSession.query(cls).filter(cls.login==login).first()

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username==username).first()

    @classmethod
    def get_by_email(cls, email):
        return DBSession.query(cls).filter(cls.email==email).first()

    @classmethod
    def check_password(cls, **kwargs):
        if kwargs.has_key('id'):
            user = cls.get_by_id(kwargs['id'])
        if kwargs.has_key('username'):
            user = cls.get_by_username(kwargs['username'])

        if not user:
            return False
        if bcrypt.hashpw(kwargs['password'], user.password) == user.password:
            return True
        else:
            return False

def populate():
    session = DBSession()
    group = AuthGroup(name=u'users')
    session.add(group)
    group = AuthGroup(name=u'admin')
    session.add(group)
    session.flush()
    transaction.commit()

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    SQLBase.metadata.bind = engine
    SQLBase.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()
