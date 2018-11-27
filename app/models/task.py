from sqlalchemy import Column, Integer, String, Text, ForeignKey, text
from sqlalchemy_utils import UUIDType
from sqlalchemy.dialects.postgresql import JSONB
from .user import User
from ..utils.db import Base

class Task(Base):
    __tablename__ = 'task'
    id = Column(UUIDType(binary=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    title = Column(String(60), nullable=False)
    description = Column(String(200))
    code = Column(Text)
    data = Column(JSONB)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    period = Column(Integer)

    def __repr__(self):
        return '<Task %r>' % self.title