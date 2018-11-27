from ..utils.db import Base
from sqlalchemy_utils import UUIDType
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128))
    tasks = relationship('Task', backref='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.username
