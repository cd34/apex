from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from apex.models import AuthUser
""" To Extend the User Model, make sure you import AuthUser in your
model.py
"""

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class ExtendedProfile(AuthUser):
    __mapper_args__ = {'polymorphic_identity': 'profile'}
    
    first_name = Column(Unicode(80))
    last_name = Column(Unicode(80))
    

class ForeignKeyProfile(Base):
    """ We're extending AuthUser by adding a Foreign Key to Profile. 
    Make sure you set index=True on user_id.
    """
    __tablename__ = 'auth_user_profile'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(AuthUser.id), index=True)
    user = relationship(AuthUser, backref=backref('profile', uselist=False))

    """ Everything below this point can be customized. In your templates, 
    you can access the user object through the request context as 

    **request.user** or **request.user.profile.firstname**
    """
    first_name = Column(Unicode(80))
    last_name = Column(Unicode(80))

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
