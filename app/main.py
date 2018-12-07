import json
import subprocess
import sys
import re
import select
import signal
from datetime import datetime
from sqlalchemy import text

from app.config import app_config
from app.utils.db import init_trigger
from app.utils.schedule import ScheduleThread
from app.utils.execute import execute
from app.utils.execute_docker import excute_with_docker

scheduler = ScheduleThread()

def keyboardInterruptHandler(signal, frame):
    """Handler for keyboardInterrupt, stop all threads and clean up"""
    scheduler.stop()
    print("KeyboardInterrupt has been caught. Cleaning up...")
    exit(0)

# Register the handler
signal.signal(signal.SIGINT, keyboardInterruptHandler)

def run_app(mode):
    """Run the app with the given mode"""
    print("Scheduler running...")
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
                scheduler.add.every(task['period']).seconds.do(excute_with_docker, task)
        #else:
            #print("time out")

if __name__ == "__main__":
    run_app('testing')