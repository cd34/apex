import bcrypt

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from sqlalchemy import *
from sqlalchemy.databases import mysql
from sqlalchemy.orm import relation, backref, synonym

user_group_table = Table('auth_user_groups', Base.metadata,
    Column('user_id', mysql.BIGINT(20, unsigned=True), ForeignKey('auth_users.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('group_id', mysql.BIGINT(20, unsigned=True), ForeignKey('auth_groups.id', onupdate='CASCADE', ondelete='CASCADE'))
)

class AuthGroup(Base):
    __tablename__ = 'auth_groups'

    id = Column(mysql.BIGINT(20, unsigned=True), primary_key=True, autoincrement=True)
    name = Column(Unicode(80), unique=True, nullable=False)
    created = Column(mysql.DATE())

    users = relation('AuthUser', secondary=user_group_table, backref='auth_groups')

    def __repr__(self):
        return '' % self.name

    def __unicode__(self):
        return self.name

class AuthUser(Base):
    __tablename__ = 'auth_users'

    """
    login is the hashed ID or username if it is a local login
    username is the display username
    """
    id = Column(mysql.BIGINT(20, unsigned=True), primary_key=True, autoincrement=True)
    login = Column(Unicode(80), nullable=False)
    username = Column(Unicode(80), nullable=False)
    _password = Column('password', Unicode(80), nullable=False)
    email = Column(Unicode(80), nullable=False)

    groups = relation('AuthGroup', secondary=user_group_table, backref='auth_users')

    @property
    def permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, password):
        self._password = bcrypt.hashpw(password, bcrypt.gensalt())

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password))

    def validate_password(self, password):
        return bcrypt.hashpw(password, self.password) == self.password

    """
    def __repr__(self):
        return '' % (self.id, self.username, self.email)
    """

    def __unicode__(self):
        return self.username

