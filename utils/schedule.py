from functools import wraps
import schedule
import threading
import time

class ScheduleThread(threading.Thread):
    def __init__(self):
        super(ScheduleThread, self).__init__()
        self.scheduler = schedule
        self.cease_continuous_run = threading.Event()

    def run(self):
        while not self.cease_continuous_run.is_set():
            self.scheduler.run_pending()
            time.sleep(1)
    
    def stop(self):
        self.cease_continuous_run.set()
    
    @property
    def add(self):
        return self.scheduler

def catch_exceptions(job_func, cancel_on_failure=False):
    @wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
            if cancel_on_failure:
                return schedule.CancelJob
    return wrapper

def with_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('LOG: Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        print('LOG: Job "%s" completed' % func.__name__)
        return result
    return wrapper