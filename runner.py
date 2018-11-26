import json
import subprocess
import sys
import re
import functools
from sqlalchemy import create_engine, text
import select
import threading
import time
import utils
import signal
from utils import ScheduleThread
from config import app_config

scheduler = ScheduleThread()

def keyboardInterruptHandler(signal, frame):
    scheduler.stop()
    print("KeyboardInterrupt has been caught. Cleaning up...")
    exit(0)

signal.signal(signal.SIGINT, keyboardInterruptHandler)

@utils.catch_exceptions
@utils.with_logging
def execute(task):
    module, offset = create_module(task['code'])
    # executable binary for the Python interpreter
    with subprocess.Popen([sys.executable, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        communicate(process, task, module, offset)

def test_job():
    print('this is job')

def create_module(code):
    lines = ["import json"]
    offset = len(lines) + 1
    outputLine = "\nprint(json.dumps(result))"
    return "\n".join(lines) + "\n" + code + outputLine, offset

def communicate(process, task, module, offset):
    stdout, stderr = process.communicate(module.encode('utf-8'))
    if stderr:
        stderr = stderr.decode('utf-8').lstrip().replace(", in <module>", ":")
        stderr = re.sub(r", line(\d+)", lambda match: str(int(match.group(1)) - offset), stderr)
        print(re.sub(r'File."[^"]+?"', "'{}' has an error on line ".format(task['title']), stderr))
        return
    if stdout:
        result = json.loads(stdout.decode("utf-8"))
        print(result)
        #report(task, result, error)
        return
    print("'{}' produced no result\n".format(task['title']))

class Map(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

if __name__ == "__main__":
    cfg = app_config['testing']
    engine = create_engine(cfg.SQLALCHEMY_DATABASE_URI)
    db = engine.connect()
    db.execute(text("LISTEN data;").execution_options(autocommit=True))
    conn = db.connection

    scheduler.start()

    while 1:
        if select.select([conn],[],[],5) != ([],[],[]): # else not ready
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print("{}\n{}\n{}".format(notify.pid, notify.channel, notify.payload))
                scheduler.add.every(10).seconds.do(get_task_by_id(notify.payload))
        #else:
            #print("time out")