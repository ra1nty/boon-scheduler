import json
import subprocess
import sys
import re
import schedule
import functools
from sqlalchemy import create_engine, text
import select
def catch_exceptions(job_func, cancel_on_failure=False):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
            if cancel_on_failure:
                return schedule.CancelJob
    return wrapper

def execute(task):
    module, offset = create_module(task.code)
    # executable binary for the Python interpreter
    with subprocess.Popen([sys.executable, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        communicate(process, task, module, offset)

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
        print(re.sub(r'File."[^"]+?"', "'{}' has an error on line ".format(task.title), stderr))
        return
    if stdout:
        result = json.loads(stdout.decode("utf-8"))
        print(result)
        #report(task, result, error)
        return
    print("'{}' produced no result\n".format(task.title))

class Map(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

if __name__ == "__main__":
    from config import app_config
    cfg = app_config['development']
    engine = create_engine(cfg.SQLALCHEMY_DATABASE_URI)
    db = engine.connect()
    db.execute(text("LISTEN data;").execution_options(autocommit=True))
    conn = db.connection
    while 1:
        #db.commit()
        if select.select([conn],[],[],6) != ([],[],[]): # else not ready
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print("{}\n{}\n{}".format(notify.pid, notify.channel, notify.payload))
    #for line in sys.stdin:
    #    execute(Map(json.loads(line)))
    # End of stream!
    #print('end')