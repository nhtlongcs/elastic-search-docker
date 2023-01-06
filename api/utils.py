
from datetime import datetime

def time_this(func):
    def calc_time(*args, **kwargs):
        before = datetime.now()
        x = func(*args, **kwargs)
        after = datetime.now()
        print("Function {} elapsed time: {}".format(func.__name__, after-before))
        return x
    return calc_time
