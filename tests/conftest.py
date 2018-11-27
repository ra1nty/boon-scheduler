import pytest
import signal
from multiprocessing import Process, Queue
from app.main import run_app
from app.utils.db import session_scope, init_testing_session, Base
from app.models.user import User
from app.models.task import Task


app_process = Process(target=run_app, args=('testing',))

@pytest.fixture(autouse=True, scope='session')
def init_tests():
    print("init_db")
    app_process.start()
    import time
    time.sleep(5)
    init_testing_session()
    with session_scope() as session:
        user = User(username = "testuser1", email = "testuser1@illinois.edu", password='random')
        session.add(user)
        test = Task(title = "test1", 
            description = "test1",
            code = "\nresult=[12.34, 32.56]\n\n",
            owner_id = 1,
            data = [],
            period = 10
        )
        testcode2 = [
            'from datetime import datetime',
            'result["time"] = str(datetime.now())',
            '#print(str(datetime.now()))'
        ]
        test2 = Task(title = "test2", 
            description = "test2",
            code = "\n".join(testcode2),
            owner_id = 1,
            data = [],
            period = 30
        )
        session.add(test)
        session.add(test2)

def pytest_sessionfinish(session, exitstatus):
    app_process.join()
    print("Dropping tables")
    Base.metadata.drop_all()

def keyboardInterruptHandler(sig, frame):
    """Handler for keyboardInterrupt, stop all threads and clean up"""
    app_process.join()
    print("Dropping tables")
    Base.metadata.drop_all()
    exit(0)

# Register the handler
signal.signal(signal.SIGINT, keyboardInterruptHandler)