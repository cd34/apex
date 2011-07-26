import bcrypt
import transaction

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy.databases import mysql

from zope.sqlalchemy import ZopeTransactionExtension 

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

user_group_table = Table('auth_user_groups', Base.metadata,
    Column('user_id', mysql.BIGINT(20, unsigned=True), \
        ForeignKey('auth_users.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('group_id', mysql.BIGINT(20, unsigned=True), \
        ForeignKey('auth_groups.id', onupdate='CASCADE', ondelete='CASCADE'))
)

class AuthGroup(Base):
    __tablename__ = 'auth_groups'

    id = Column(mysql.BIGINT(20, unsigned=True), primary_key=True, \
                autoincrement=True)
    name = Column(Unicode(80), unique=True, nullable=False)
    created = Column(mysql.DATE(), default=func.curdate())

    users = relation('AuthUser', secondary=user_group_table, \
                     backref='auth_groups')

    def __repr__(self):
        return '' % self.name

    def __unicode__(self):
        return self.name

class AuthUser(Base):
    __tablename__ = 'auth_users'

    id = Column(mysql.BIGINT(20, unsigned=True), primary_key=True, \
                autoincrement=True)
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
    try:
        populate()
    except IntegrityError:
        transaction.abort()
