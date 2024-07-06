"""
All the packed universal functions were stored here.
"""
def isFuncFromModule(func: types.FunctionType, module: str):
    return func.__module__.startswith(module);
isFuncFromModule(torch.nn.LSTM, "torch")


def getAttributes(module: str):
    return [i for i in dir(module) if "__" not in i];
getAttributes(torch.optim)


def getAPIName(func):
    apiName = func.__module__;
    if func.__name__[-len(func.__name__)+1:] == apiName[-len(func.__name__)+1:]:
        apiName = apiName[:-len(func.__name__)] + func.__name__;
    else:
        apiName = apiName + "." + func.__name__;
    return apiName;
getAPIName(torch.optim.Adam),getAPIName(torch.mul)


def isDecorated(func: types.FunctionType):
    if hasattr(func, "isDecorated"):
        return True;
    else: 
        return False;
isDecorated(torch.tensor)
