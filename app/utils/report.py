from sqlalchemy.orm.attributes import flag_modified
from .db import session_scope
from ..models.task import Task

def report(task, result):
    with session_scope() as session:
        tsk = session.query(Task).filter(Task.id == task['id']).first()
        tsk.data.append(result)
        flag_modified(tsk, "data")
        print(tsk.data)
        session.add(tsk)