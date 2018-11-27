import json
import subprocess
import sys
import re
import select
import signal
from datetime import datetime
from sqlalchemy import text

from .config import app_config
from .utils.schedule import ScheduleThread, catch_exceptions, with_logging
from .utils.db import init_trigger
from .utils.report import report

scheduler = ScheduleThread()

def keyboardInterruptHandler(signal, frame):
    """Handler for keyboardInterrupt, stop all threads and clean up"""
    scheduler.stop()
    print("KeyboardInterrupt has been caught. Cleaning up...")
    exit(0)

# Register the handler
signal.signal(signal.SIGINT, keyboardInterruptHandler)

@catch_exceptions
@with_logging
def execute(task):
    module, offset = create_module(task['code'])
    # executable binary for the Python interpreter
    with subprocess.Popen([sys.executable, '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
        communicate(process, task, module, offset)

def create_module(code):
    lines = ["import json", "result = dict()"]
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
        report(task, result)
        return
    print("'{}' produced no result\n".format(task['title']))

def run_app(mode):
    """Run the app with the given mode"""
    conn = init_trigger(mode)
    scheduler.start()

    while 1:
        if select.select([conn],[],[],5) != ([],[],[]): # else not ready
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                #print("{}\n{}\n{}".format(notify.pid, notify.channel, notify.payload))
                task = json.loads(notify.payload)
                print("{}\n New task : {}".format(str(datetime.now()),task['title']))
                scheduler.add.every(task['period']).seconds.do(execute, task)
        #else:
            #print("time out")

if __name__ == "__main__":
    run_app('testing')