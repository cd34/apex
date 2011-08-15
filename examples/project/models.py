import transaction

from sqlalchemy import Column
from sqlalchmey import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from velruse.store.sqlstore import KeyStorage
from velruse.store.sqlstore import SQLBase

from pyramid_apex.models import AuthUser

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

class ExtendedProfile(AuthUser):
    __mapper_args__ = {'polymorphic_identity': 'profile'}
    
    first_name = Column(Unicode(80))
    last_name = Column(Unicode(80))
    
class ForeignKeyProfile(Base):
    __tablename__ = 'auth_user_profile'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(AuthUser.id))
    first_name = Column(Unicode(80))
    last_name = Column(Unicode(80))

    user = relationship('AuthUser', backref=backref('profile', uselist=False))

def populate():
    session = DBSession()
    model = MyModel(name=u'root', value=55)
    session.add(model)
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
