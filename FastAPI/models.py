from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))

class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    user_id = Column(Integer)
    image_url = Column(String(255))
    description = Column(String(100))
    likes = Column(Integer)

class Story(Base):
    __tablename__ = 'stories'
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, index=True)
    username = Column(String, index=True)
    

   