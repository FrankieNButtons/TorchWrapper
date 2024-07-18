# import necessary modules
import functools;
import time;
import types;
import warnings;
from .apitools import *;



# TimeDecorator
def TimerDecorator(func: types.FunctionType):
    """
    **Description**
    A running timer for a function.
    
    **params**
    func(String): the function to be timed.
    
    **returns**
    wrapper: a timer decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        startTime = time.perf_counter_ns();
        result = func(*args, **kwargs);
        endTime = time.perf_counter_ns();
        costTime = (endTime - startTime) / 1000 / 1000;
        timeLog = f"{func.__name__}() cost {costTime} ms";
        # print(timeLog);
        return result, startTime, costTime;
    return wrapper;


# APIdecorator
def APIDecorator(func: str, module: str=None):
    """
    **Description**
    A API usage recorder for a function.
    
    **params**
    func(String): the function to be recorded.
    
    **returns**
    wrapper: a API usage recored function.
    """
    apiName = getAPIName(func)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        apiName = getAPIName(func)
        result, startTimestamp, costTime= TimerDecorator(func)(*args, **kwargs);
        print(f"{apiName} starts from {startTimestamp} costs {costTime}ms.");
        return result, apiName, startTimestamp, costTime;
    if module == None:
        return wrapper;
    elif isFromModule(func, module):
        return wrapper;
    else:
        # raise ValueError(f"the function `{apiName}` is not from module `{module}`");
        return func;


