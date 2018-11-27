from functools import wraps
import schedule
import threading
import time

class ScheduleThread(threading.Thread):
    """A wrapper class to run the schedule in a separate thread

    This class is implemented as a Thread, with ....

    Attributes:
        scheduler: Default scheduler from the schedule library
        cease_continuous_run: An event serve as a stop flag
    """
    def __init__(self):
        """Init ScheduleThread class"""
        super(ScheduleThread, self).__init__()
        self.scheduler = schedule
        self.cease_continuous_run = threading.Event()

    def run(self):
        """The run protocol for Thread"""
        while not self.cease_continuous_run.is_set():
            self.scheduler.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the thread"""
        self.cease_continuous_run.set()
    
    @property
    def add(self):
        """Helper method for adding task"""
        return self.scheduler

def catch_exceptions(job_func, cancel_on_failure=False):
    """Decorator for the catch exception utility in scheduler
    Args:
        job_func: the original function being wrapped
        cancel_on_failure: if set to True, job will be canceled
            if an exception occured
    """
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
    """Decorator for the logging utility in scheduler"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('LOG: Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        print('LOG: Job "%s" completed' % func.__name__)
        return result
    return wrapper