import bcrypt

from sqlalchemy import Column, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation, backref, synonym
from sqlalchemy.databases import mysql

from zope.sqlalchemy import ZopeTransactionExtension 

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class AuthUser(Base):
    __tablename__ = 'auth_users'

    id = Column(mysql.BIGINT(20, unsigned=True), primary_key=True, autoincrement=True)
    username = Column(Unicode(80), nullable=False)
    _password = Column('password', Unicode(80), nullable=False)
    email = Column(Unicode(80), nullable=False)

    def _set_password(self, password):
        self._password = bcrypt.hashpw(password, bcrypt.gensalt())

    def _get_password(self):
        return self._password

    password = synonym('_password', descriptor=property(_get_password, _set_password))
    
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()    

    @classmethod
    def get_by_username(cls, username):
        return DBSession.query(cls).filter(cls.username==username).first()

    @classmethod
    def get_by_email(cls, email):
        return DBSession.query(cls).filter(cls.email==email).first()

    @classmethod
    def check_password(cls, id=None, username=None, password=None):
        if id and username:
            return False
        if not password:
            return False
        if id:
            user = cls.get_by_id(id)
        if username:
            user = cls.get_by_username(username)

        if not user:
            return False
        if bcrypt.hashpw(password, user.password) == user.password:
            return True
        else:
            return False

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
