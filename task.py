from datetime import datetime
from app import db, ma
from sqlalchemy_utils import UUIDType
import sqlalchemy

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(UUIDType(binary=True), primary_key=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    title = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(200))
    data = db.Column(db.LargeBinary)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.
    def __repr__(self):
        return '<Post %r>' % self.title

class TaskSchema(ma.ModelSchema):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'data', 'owner_id')

task

id
title
description
code
result
owner_id
created_at
status
period
last_run

https://gist.github.com/bruth/6d53a3c2138c5adf53f5

class Map(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
